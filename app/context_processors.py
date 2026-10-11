from flask import current_app


def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        return {
            'institution_name': current_app.config.get('INSTITUTION_NAME', 'College'),
        }
