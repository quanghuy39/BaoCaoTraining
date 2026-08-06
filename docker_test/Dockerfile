# Sử dụng Image chính thức của MySQL 8.4
FROM mysql:8.4

# Đặt mật khẩu root cho MySQL
ENV MYSQL_ROOT_PASSWORD=quanghuy0309

# Tự động Copy file SQL vào thư mục khởi tạo tự động của MySQL Container
COPY ./classicmodels.sql /docker-entrypoint-initdb.d/

# Mở cổng 3306 để ứng dụng kết nối
EXPOSE 3306

