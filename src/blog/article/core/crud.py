from flask import jsonify

from src.database import get_db_connection


def fetch_articles(query, params):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute(query, params)
            article_info = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM `articles` WHERE `Hidden`=0 AND `Status`='Published'")
            total_articles = cursor.fetchone()[0]

    except Exception as e:
        print(f"Error getting articles: {e}")
        raise

    finally:
        if db is not None:
            db.close()
        return article_info, total_articles


def get_articles_by_owner(owner_id=None):
    db = get_db_connection()
    articles = []

    try:
        with db.cursor() as cursor:
            if owner_id:
                query = """
                        SELECT a.article_id, a.Title
                        FROM articles AS a
                        WHERE a.user_id = %s
                          and a.`Status` != 'Deleted'; \
                        """
                cursor.execute(query, (owner_id,))
                articles.extend((result[0], result[1]) for result in cursor.fetchall())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
        return articles


def get_articles_recycle(user_id):
    db = get_db_connection()
    articles = []

    try:
        with db.cursor() as cursor:
            if user_id:
                query = """
                        SELECT a.article_id, a.Title
                        FROM articles AS a
                        WHERE a.user_id = %s
                          and a.`Status` = 'Deleted'; \
                        """
                cursor.execute(query, (user_id,))
                articles.extend((result[0], result[1]) for result in cursor.fetchall())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

    return articles


def delete_db_article(user_id, aid):
    try:
        with get_db_connection() as db:
            with db.cursor() as cursor:
                cursor.execute("UPDATE `articles` SET Hidden=1, `Status`=%s WHERE `article_id`=%s", ('Deleted', aid))
                db.commit()
        return jsonify({'show_edit_code': "deleted"}), 201
    except Exception as e:
        return jsonify({'show_edit_code': 'error', 'message': f'删除文章失败{e}'}), 500


def get_id_by_title(title):
    try:
        with get_db_connection() as db:
            with db.cursor() as cursor:
                query = "SELECT `article_id` FROM `articles` WHERE `title`=%s and `Hidden`=0 and `Status`='Published'"
                cursor.execute(query, (title,))
                result = cursor.fetchone()
                if result:
                    return result[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        # 更详细的日志记录或错误处理机制

    return None


def fetch_articles_content(aid):
    try:
        with get_db_connection() as db:
            with db.cursor() as cursor:
                query = "SELECT `content` FROM `article_content` WHERE `aid`=%s"
                cursor.execute(query, (aid,))
                result = cursor.fetchone()
                if result:
                    return result[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        # 更详细的日志记录或错误处理机制
        return None


def get_article_last_modified(title):
    try:
        # 创建数据库连接
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # 假设通过文章的ID来查找文章
            query = "SELECT updated_at FROM articles WHERE title = %s"
            cursor.execute(query, (title,))
            result = cursor.fetchone()

            if result and 'updated_at' in result:
                modify_time = result['updated_at']
                formatted_modify_time = modify_time.strftime("%Y-%m-%d %H:%M")
                return formatted_modify_time
            else:
                return None

    except Exception as e:
        # 处理数据库连接或查询错误
        print(f"发生错误: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
