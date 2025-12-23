from flask import Blueprint, render_template_string
from repositories.factory import RepositoryFactory

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', strict_slashes=False)
def users():
    try:
        user_repo = RepositoryFactory.get_user_repository()
        users = user_repo.get_all()
    except Exception:
        # Return 500 when repository raises an exception
        return 'Internal Server Error', 500

    if not users:
        return render_template_string('<h1>No users found</h1>'), 404
    output = '<ul>'
    for u in users:
        name = getattr(u, 'name', str(u))
        output += f'<li>{name}</li>'
    output += '</ul>'
    return render_template_string(output)
