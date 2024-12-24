import mysql.connector
from mysql.connector import Error

class DatabaseHelper:
    @staticmethod
    def getConnection():
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='teashop',
                user='root',
                password=''
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error: {e}")
        return None

    @staticmethod
    def getUserByEmailAndPassword(email, password):
        query = "SELECT * FROM users WHERE email = %s AND password_hash = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def registerUser(email, password, fullName, phone):
        insertQuery = "INSERT INTO users (email, password_hash, full_name, phone, role) VALUES (%s, %s, %s, %s, 'customer')"
        selectQuery = "SELECT * FROM users WHERE email = %s AND password_hash = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(insertQuery, (email, password, fullName, phone))
        connection.commit()
        cursor.execute(selectQuery, (email, password))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getUserById(userId):
        query = "SELECT * FROM users WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (userId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getAllTeas(role):
        query = "SELECT * FROM teas WHERE stock > 0"
        if role == "admin":
            query = "SELECT * FROM teas"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getTeaById(teaId):
        query = "SELECT * FROM teas WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (teaId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getCartItemsByUserId(userId, role):
        if role == "customer":
            query = """
            SELECT t.id, t.name, c.quantity, t.price, t.image_path
            FROM order_tea c
            JOIN teas t ON c.tea_id = t.id
            WHERE c.order_id = (SELECT id FROM orders WHERE user_id = %s LIMIT 1)
            """
        elif role == "admin":
            query = """
            SELECT t.id, t.name, c.quantity, t.price, t.image_path
            FROM admin_order_tea c
            JOIN teas t ON c.tea_id = t.id
            WHERE c.admin_order_id = (SELECT id FROM admin_orders WHERE admin_id = %s LIMIT 1)
            """
        else:
            return []
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (userId,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def updateUserProfile(userId, fullName, phone):
        query = "UPDATE users SET full_name = %s, phone = %s WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (fullName, phone, userId))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def updateUserEmail(userId, email):
        query = "UPDATE users SET email = %s WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (email, userId))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def getBrandById(brandId):
        query = "SELECT * FROM brands WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (brandId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getSupplierById(supplierId):
        query = "SELECT id, name, contact_info, YEAR(created_at) as created_year FROM suppliers WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (supplierId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getTeaStock(teaId):
        query = "SELECT stock FROM teas WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (teaId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result['stock'] if result else 0

    @staticmethod
    def addToCart(userId, teaId, quantity):
        currentStock = DatabaseHelper.getTeaStock(teaId)
        if currentStock < quantity:
            raise ValueError("Not enough stock available.")

        query = ""
        if DatabaseHelper.getUserRoleById(userId) == "customer":
            orderId = DatabaseHelper.getOrderIdByUserId(userId)
            if orderId == -1:
                DatabaseHelper.createOrderForUser(userId)
                orderId = DatabaseHelper.getOrderIdByUserId(userId)
            query = "INSERT INTO order_tea (order_id, tea_id, quantity) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + %s"
        elif DatabaseHelper.getUserRoleById(userId) == "admin":
            adminOrderId = DatabaseHelper.getAdminOrderIdByAdminId(userId)
            if adminOrderId == -1:
                DatabaseHelper.createAdminOrderForAdmin(userId)
                adminOrderId = DatabaseHelper.getAdminOrderIdByAdminId(userId)
            query = "INSERT INTO admin_order_tea (admin_order_id, tea_id, quantity) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + %s"
        else:
            raise ValueError("Invalid user role")

        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        if DatabaseHelper.getUserRoleById(userId) == "customer":
            cursor.execute(query, (orderId, teaId, quantity, quantity))
        elif DatabaseHelper.getUserRoleById(userId) == "admin":
            cursor.execute(query, (adminOrderId, teaId, quantity, quantity))
        connection.commit()
        cursor.close()
        connection.close()

        DatabaseHelper.updateTeaStock(teaId, quantity)

    @staticmethod
    def removeFromCart(userId, teaId, quantity):
        query = ""
        if DatabaseHelper.getUserRoleById(userId) == "customer":
            query = "DELETE FROM order_tea WHERE order_id = (SELECT id FROM orders WHERE user_id = %s LIMIT 1) AND tea_id = %s AND quantity = %s LIMIT 1"
        elif DatabaseHelper.getUserRoleById(userId) == "admin":
            query = "DELETE FROM admin_order_tea WHERE admin_order_id = (SELECT id FROM admin_orders WHERE admin_id = %s LIMIT 1) AND tea_id = %s AND quantity = %s LIMIT 1"
        else:
            raise ValueError("Invalid user role")

        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (userId, teaId, quantity))
        connection.commit()
        cursor.close()
        connection.close()

        # Возвращаем количество товара на склад
        DatabaseHelper.returnTeaStock(teaId, quantity)

    @staticmethod
    def returnTeaStock(teaId, quantity):
        query = "UPDATE teas SET stock = stock + %s WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (quantity, teaId))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def updateTeaStock(teaId, quantity):
        query = "UPDATE teas SET stock = stock - %s WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (quantity, teaId))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def getOrderIdByUserId(userId):
        query = "SELECT id FROM orders WHERE user_id = %s LIMIT 1"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (userId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result['id'] if result else -1

    @staticmethod
    def createOrderForUser(userId):
        query = "INSERT INTO orders (user_id, status) VALUES (%s, 'В ожидании')"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (userId,))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def getAdminOrderIdByAdminId(adminId):
        query = "SELECT id FROM admin_orders WHERE admin_id = %s LIMIT 1"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (adminId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result['id'] if result else -1

    @staticmethod
    def createAdminOrderForAdmin(adminId):
        query = "INSERT INTO admin_orders (admin_id, status) VALUES (%s, 'В ожидании')"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (adminId,))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def getUserRoleById(userId):
        query = "SELECT role FROM users WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (userId,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result['role'] if result else None

    @staticmethod
    def updateCartItemQuantity(userId, teaId, quantity):
        query = ""
        if DatabaseHelper.getUserRoleById(userId) == "customer":
            query = "UPDATE order_tea SET quantity = %s WHERE order_id = (SELECT id FROM orders WHERE user_id = %s LIMIT 1) AND tea_id = %s"
        elif DatabaseHelper.getUserRoleById(userId) == "admin":
            query = "UPDATE admin_order_tea SET quantity = %s WHERE admin_order_id = (SELECT id FROM admin_orders WHERE admin_id = %s LIMIT 1) AND tea_id = %s"
        else:
            raise ValueError("Invalid user role")

        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        if DatabaseHelper.getUserRoleById(userId) == "customer":
            cursor.execute(query, (quantity, userId, teaId))
        elif DatabaseHelper.getUserRoleById(userId) == "admin":
            cursor.execute(query, (quantity, userId, teaId))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def getUserOrders(userId):
        query = "SELECT id, order_date, status FROM orders WHERE user_id = %s AND status = 'Подтверждено'"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (userId,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getOrderDetails(orderId):
        query = """
        SELECT t.name, ot.quantity, t.price
        FROM order_tea ot
        JOIN teas t ON ot.tea_id = t.id
        WHERE ot.order_id = %s
        """
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (orderId,))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def confirmOrder(userId, role):
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()

        try:
            if role == "customer":
                # Получаем текущий заказ
                currentOrderIdQuery = "SELECT id FROM orders WHERE user_id = %s AND status = 'В ожидании' LIMIT 1"
                cursor.execute(currentOrderIdQuery, (userId,))
                currentOrderId = cursor.fetchone()

                if currentOrderId:
                    currentOrderId = currentOrderId[0]

                    # Обновляем статус текущего заказа на "Подтверждено"
                    query = "UPDATE orders SET status = 'Подтверждено' WHERE id = %s"
                    cursor.execute(query, (currentOrderId,))
                    connection.commit()

                    # Создаем новый заказ со статусом "В ожидании"
                    query = "INSERT INTO orders (user_id, status) VALUES (%s, 'В ожидании')"
                    cursor.execute(query, (userId,))
                    connection.commit()
                else:
                    raise ValueError("Текущий заказ не найден")

            elif role == "admin":
                # Получаем текущий заказ
                currentOrderIdQuery = "SELECT id FROM admin_orders WHERE admin_id = %s AND status = 'В ожидании' LIMIT 1"
                cursor.execute(currentOrderIdQuery, (userId,))
                currentOrderId = cursor.fetchone()

                if currentOrderId:
                    currentOrderId = currentOrderId[0]

                    # Обновляем статус текущего заказа на "Подтверждено"
                    query = "UPDATE admin_orders SET status = 'Подтверждено' WHERE id = %s"
                    cursor.execute(query, (currentOrderId,))
                    connection.commit()

                    # Создаем новый заказ со статусом "В ожидании"
                    query = "INSERT INTO admin_orders (admin_id, status) VALUES (%s, 'В ожидании')"
                    cursor.execute(query, (userId,))
                    connection.commit()
                else:
                    raise ValueError("Текущий заказ не найден")

        except Exception as e:
            print(f"Ошибка при подтверждении заказа: {e}")
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def clearCart(userId, role):
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()

        try:
            if role == "customer":
                # Удаляем все записи из order_tea для текущего пользователя
                query = "DELETE FROM order_tea WHERE order_id = (SELECT id FROM orders WHERE user_id = %s AND status = 'Подтверждено' LIMIT 1)"
                cursor.execute(query, (userId,))
                connection.commit()

                # Создаем новый заказ со статусом "В ожидании"
                query = "INSERT INTO orders (user_id, status) VALUES (%s, 'В ожидании')"
                cursor.execute(query, (userId,))
                connection.commit()

            elif role == "admin":
                # Удаляем все записи из admin_order_tea для текущего администратора
                query = "DELETE FROM admin_order_tea WHERE admin_order_id = (SELECT id FROM admin_orders WHERE admin_id = %s AND status = 'В ожидании' LIMIT 1)"
                cursor.execute(query, (userId,))
                connection.commit()

                # Создаем новый заказ со статусом "В ожидании"
                query = "INSERT INTO admin_orders (admin_id, status) VALUES (%s, 'В ожидании')"
                cursor.execute(query, (userId,))
                connection.commit()

        except Exception as e:
            print(f"Ошибка при очистке корзины: {e}")
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def getAllOrders():
        query = "SELECT id, order_date, status FROM orders"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def updateOrderStatus(orderId, status):
        query = "UPDATE orders SET status = %s WHERE id = %s"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (status, orderId))
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def getAllBrands():
        query = "SELECT id, name FROM brands"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def getAllSuppliers():
        query = "SELECT id, contact_info FROM suppliers"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def addTea(name, brandId, supplierId, price, stock, imagePath):
        query = "INSERT INTO teas (name, brand_id, supplier_id, price, stock, image_path) VALUES (%s, %s, %s, %s, %s, %s)"
        connection = DatabaseHelper.getConnection()
        cursor = connection.cursor()
        cursor.execute(query, (name, brandId, supplierId, price, stock, imagePath))
        connection.commit()
        cursor.close()
        connection.close()