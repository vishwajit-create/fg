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
        tb = traceback.format_exc()
        app.logger.error(f'Server Error: {e}\n{tb}')
        return f"<div id='server-error-trace' style='display:block;background:#fee;border:1px solid red;padding:15px;margin:20px;font-family:monospace;'><h3>[DEBUG ERROR] {type(e).__name__}: {e}</h3><pre>{tb}</pre></div>" + render_template('errors/500.html'), 500
