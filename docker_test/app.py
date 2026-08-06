import sys
import pymysql
import pymysql.cursors
from tabulate import tabulate
 
# ==========================================
# 1. CẤU HÌNH KẾT NỐI
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'quanghuy0309',
    'database': 'classicmodels',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True
}
 
 
def get_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.Error as e:
        print(f"\n❌ Lỗi kết nối: {e}")
        sys.exit(1)
 
 
# ==========================================
# 2. TIỆN ÍCH DÙNG CHUNG
# ==========================================
def run_query(sql, params=None):
    """Thực thi câu SELECT và trả về danh sách dict."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    except pymysql.Error as e:
        print(f"\n❌ Lỗi truy vấn: {e}")
        return []
    finally:
        conn.close()
 
 
def run_write(sql, params=None):
    """Thực thi INSERT / UPDATE / DELETE. Trả về số dòng bị ảnh hưởng."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount
    except pymysql.Error as e:
        print(f"\n❌ Lỗi thực thi: {e}")
        return -1
    finally:
        conn.close()
 
 
def show_table(rows):
    if not rows:
        print("\n(Không có dữ liệu phù hợp)")
        return
    print("\n" + tabulate(rows, headers="keys", tablefmt="fancy_grid", floatfmt=".2f"))
    print(f"=> {len(rows)} dòng kết quả.\n")
 
 
def ask(prompt, cast=str, allow_empty=False):
    while True:
        raw = input(prompt).strip()
        if raw == "" and allow_empty:
            return None
        try:
            return cast(raw)
        except ValueError:
            print("⚠️  Giá trị không hợp lệ, vui lòng nhập lại.")
 
 
def pause():
    input("\nNhấn Enter để tiếp tục...")
 
 
# ==========================================
# 3. QUẢN LÝ KHÁCH HÀNG (customers)
# ==========================================
def list_customers():
    """SELECT ... WHERE ... ORDER BY"""
    kw = ask("Nhập quốc gia để lọc (bỏ trống để xem tất cả): ", allow_empty=True)
    if kw:
        sql = """
            SELECT customerNumber, customerName, city, country, creditLimit
            FROM customers
            WHERE country LIKE %s
            ORDER BY customerName
        """
        show_table(run_query(sql, (f"%{kw}%",)))
    else:
        sql = """
            SELECT customerNumber, customerName, city, country, creditLimit
            FROM customers
            ORDER BY customerName
            LIMIT 30
        """
        show_table(run_query(sql))
 
 
def add_customer():
    """INSERT"""
    print("\n--- Thêm khách hàng mới ---")
    name = ask("Tên công ty khách hàng: ")
    last = ask("Họ người liên hệ: ")
    first = ask("Tên người liên hệ: ")
    phone = ask("Số điện thoại: ")
    city = ask("Thành phố: ")
    country = ask("Quốc gia: ")
    credit = ask("Hạn mức tín dụng: ", float, allow_empty=True) or 0
 
    max_row = run_query("SELECT MAX(customerNumber) AS m FROM customers")
    new_id = (max_row[0]['m'] or 0) + 1
 
    sql = """
        INSERT INTO customers
            (customerNumber, customerName, contactLastName, contactFirstName,
             phone, addressLine1, city, country, creditLimit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    affected = run_write(sql, (new_id, name, last, first, phone, "N/A", city, country, credit))
    if affected == 1:
        print(f"✅ Đã thêm khách hàng mới, mã số: {new_id}")
 
 
def delete_customer():
    """DELETE (kiểm tra ràng buộc khóa ngoại trước khi xoá)"""
    cust_id = ask("Nhập mã khách hàng cần xoá: ", int)
    has_orders = run_query("SELECT COUNT(*) AS c FROM orders WHERE customerNumber=%s", (cust_id,))
    if has_orders[0]['c'] > 0:
        print("❌ Không thể xoá: khách hàng này đang có đơn hàng liên kết.")
        return
    confirm = ask("Bạn có chắc muốn xoá khách hàng này? (y/n): ")
    if confirm.lower() != 'y':
        print("Đã huỷ thao tác.")
        return
    affected = run_write("DELETE FROM customers WHERE customerNumber = %s", (cust_id,))
    print("✅ Đã xoá khách hàng." if affected else "⚠️  Không tìm thấy khách hàng để xoá.")
 
 
def customer_menu():
    while True:
        print("""
===== QUẢN LÝ KHÁCH HÀNG =====
1. Danh sách / tìm khách hàng theo quốc gia
2. Thêm khách hàng mới
3. Xoá khách hàng
0. Quay lại menu chính
""")
        choice = ask("Chọn chức năng: ")
        if choice == '1':
            list_customers()
        elif choice == '2':
            add_customer()
        elif choice == '3':
            delete_customer()
        elif choice == '0':
            break
        else:
            print("⚠️  Lựa chọn không hợp lệ.")
        pause()
 
 
# ==========================================
# 4. QUẢN LÝ SẢN PHẨM (products / productlines)
# ==========================================
def list_products_by_line():
    """SELECT ... WHERE ... ORDER BY"""
    line = ask("Nhập dòng sản phẩm (vd: Classic Cars, Motorcycles...): ")
    sql = """
        SELECT productCode, productName, productLine, quantityInStock, MSRP
        FROM products
        WHERE productLine LIKE %s
        ORDER BY productName
    """
    show_table(run_query(sql, (f"%{line}%",)))
 
 
def revenue_by_productline():
    """JOIN + GROUP BY + Aggregate + ORDER BY"""
    sql = """
        SELECT p.productLine,
               SUM(od.quantityOrdered) AS tongSoLuongBan,
               SUM(od.quantityOrdered * od.priceEach) AS doanhThu
        FROM products p
        JOIN orderdetails od ON p.productCode = od.productCode
        GROUP BY p.productLine
        ORDER BY doanhThu DESC
    """
    show_table(run_query(sql))
 
 
def update_product_price():
    """UPDATE"""
    code = ask("Nhập mã sản phẩm (productCode): ")
    row = run_query("SELECT productName, MSRP FROM products WHERE productCode=%s", (code,))
    if not row:
        print("⚠️  Không tìm thấy sản phẩm.")
        return
    print(f"Sản phẩm: {row[0]['productName']} | Giá MSRP hiện tại: {row[0]['MSRP']}")
    new_price = ask("Nhập giá MSRP mới: ", float)
    affected = run_write("UPDATE products SET MSRP = %s WHERE productCode = %s", (new_price, code))
    print("✅ Cập nhật giá thành công." if affected else "⚠️  Không có thay đổi nào.")
 
 
def product_menu():
    while True:
        print("""
===== QUẢN LÝ SẢN PHẨM =====
1. Danh sách sản phẩm theo dòng sản phẩm
2. Doanh thu theo dòng sản phẩm (JOIN + GROUP BY)
3. Cập nhật giá bán (MSRP)
0. Quay lại menu chính
""")
        choice = ask("Chọn chức năng: ")
        if choice == '1':
            list_products_by_line()
        elif choice == '2':
            revenue_by_productline()
        elif choice == '3':
            update_product_price()
        elif choice == '0':
            break
        else:
            print("⚠️  Lựa chọn không hợp lệ.")
        pause()
 
 
# ==========================================
# 5. QUẢN LÝ ĐƠN HÀNG (orders / orderdetails)
# ==========================================
def orders_by_customer():
    """JOIN + WHERE + ORDER BY"""
    cust_id = ask("Nhập mã khách hàng: ", int)
    sql = """
        SELECT o.orderNumber, o.orderDate, o.status, c.customerName
        FROM orders o
        JOIN customers c ON o.customerNumber = c.customerNumber
        WHERE o.customerNumber = %s
        ORDER BY o.orderDate DESC
    """
    show_table(run_query(sql, (cust_id,)))
 
 
def order_detail_view():
    """JOIN nhiều bảng"""
    order_id = ask("Nhập mã đơn hàng (orderNumber): ", int)
    sql = """
        SELECT od.productCode, p.productName, od.quantityOrdered,
               od.priceEach, (od.quantityOrdered * od.priceEach) AS thanhTien
        FROM orderdetails od
        JOIN products p ON od.productCode = p.productCode
        WHERE od.orderNumber = %s
        ORDER BY od.orderLineNumber
    """
    show_table(run_query(sql, (order_id,)))
 
 
def update_order_status():
    """UPDATE"""
    order_id = ask("Nhập mã đơn hàng cần cập nhật: ", int)
    row = run_query("SELECT status FROM orders WHERE orderNumber=%s", (order_id,))
    if not row:
        print("⚠️  Không tìm thấy đơn hàng.")
        return
    print(f"Trạng thái hiện tại: {row[0]['status']}")
    print("Các trạng thái hợp lệ: In Process, Shipped, Cancelled, Resolved, Disputed, On Hold")
    new_status = ask("Nhập trạng thái mới: ")
    affected = run_write("UPDATE orders SET status = %s WHERE orderNumber = %s", (new_status, order_id))
    print("✅ Cập nhật trạng thái thành công." if affected else "⚠️  Không có thay đổi nào.")
 
 
def order_menu():
    while True:
        print("""
===== QUẢN LÝ ĐƠN HÀNG =====
1. Xem đơn hàng theo khách hàng
2. Xem chi tiết một đơn hàng
3. Cập nhật trạng thái đơn hàng
0. Quay lại menu chính
""")
        choice = ask("Chọn chức năng: ")
        if choice == '1':
            orders_by_customer()
        elif choice == '2':
            order_detail_view()
        elif choice == '3':
            update_order_status()
        elif choice == '0':
            break
        else:
            print("⚠️  Lựa chọn không hợp lệ.")
        pause()
 
 
# ==========================================
# 6. BÁO CÁO / THỐNG KÊ
# ==========================================
def orders_by_status_report():
    """GROUP BY + Aggregate"""
    sql = """
        SELECT status, COUNT(*) AS soDon
        FROM orders
        GROUP BY status
        ORDER BY soDon DESC
    """
    show_table(run_query(sql))
 
 
def top_customers_by_payment():
    """JOIN + GROUP BY + HAVING + ORDER BY + LIMIT"""
    min_amount = ask("Tổng thanh toán tối thiểu (HAVING), vd 100000: ", float)
    sql = """
        SELECT c.customerNumber, c.customerName,
               SUM(p.amount) AS tongThanhToan
        FROM customers c
        JOIN payments p ON c.customerNumber = p.customerNumber
        GROUP BY c.customerNumber, c.customerName
        HAVING SUM(p.amount) > %s
        ORDER BY tongThanhToan DESC
        LIMIT 20
    """
    show_table(run_query(sql, (min_amount,)))
 
 
def report_menu():
    while True:
        print("""
===== BÁO CÁO / THỐNG KÊ =====
1. Thống kê số đơn hàng theo trạng thái (GROUP BY)
2. Khách hàng thanh toán nhiều nhất (JOIN + HAVING)
0. Quay lại menu chính
""")
        choice = ask("Chọn chức năng: ")
        if choice == '1':
            orders_by_status_report()
        elif choice == '2':
            top_customers_by_payment()
        elif choice == '0':
            break
        else:
            print("⚠️  Lựa chọn không hợp lệ.")
        pause()
 
 
# ==========================================
# 7. MENU CHÍNH
# ==========================================
def main_menu():
    while True:
        print("""
╔══════════════════════════════════════════════╗
║   HỆ THỐNG QUẢN LÝ BÁN HÀNG - CLASSICMODELS  ║
╚══════════════════════════════════════════════╝
1. Quản lý khách hàng
2. Quản lý sản phẩm
3. Quản lý đơn hàng
4. Báo cáo / Thống kê
0. Thoát chương trình
""")
        choice = ask("Chọn menu: ")
        if choice == '1':
            customer_menu()
        elif choice == '2':
            product_menu()
        elif choice == '3':
            order_menu()
        elif choice == '4':
            report_menu()
        elif choice == '0':
            print("Tạm biệt!")
            sys.exit(0)
        else:
            print("⚠️  Lựa chọn không hợp lệ.")
 
 
if __name__ == "__main__":
    main_menu()