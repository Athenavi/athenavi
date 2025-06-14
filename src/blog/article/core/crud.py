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
