from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, task_schema, tasks_schema

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """
    Create a new task
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: "JWT Token (Format: Bearer <token>)"
      - name: body
        in: body
        required: true
        schema:
          required:
            - title
          properties:
            title:
              type: string
            description:
              type: string
            category:
              type: string
    responses:
      201:
        description: Task created successfully.
    """
    
    data = request.get_json()
    errors = task_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    current_user_id = get_jwt_identity()
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        category=data.get('category', 'General'),
        user_id=current_user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created", "id": new_task.id}), 201

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Get all tasks for the logged-in user
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
      - name: category
        in: query
        type: string
        description: Filter tasks by category name.
    responses:
      200:
        description: A list of tasks.
    """
    
    current_user_id = get_jwt_identity()
    category = request.args.get('category')
    
    query = Task.query.filter_by(user_id=current_user_id)
    if category:
        query = query.filter_by(category=category)
    
    tasks = query.all()
    return jsonify(tasks_schema.dump(tasks)), 200

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """
    Update a task status or details
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
      - name: task_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            is_completed:
              type: boolean
    responses:
      200:
        description: Task updated successfully.
    """
    
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
    
    data = request.get_json()
    # Partial=True allows us to update only one field (e.g., just is_completed)
    errors = task_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.is_completed = data.get('is_completed', task.is_completed)
    
    db.session.commit()
    return jsonify({"message": "Task updated"}), 200

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200
