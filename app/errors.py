import traceback
from flask import render_template


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Server Error: {e}\n{traceback.format_exc()}')
        return render_template('errors/500.html'), 500
