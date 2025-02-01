import json
from flask import Flask, jsonify, request, abort


# Cargar datos desde un archivo JSON
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"categories": [], "tasks": []}

# Guardar datos en el archivo JSON
def save_data():
    with open('data.json', 'w') as file:
        json.dump({"categories": categories, "tasks": tasks}, file, indent=4)


app = Flask(__name__)
data = load_data()
categories = data["categories"] 
tasks = data["tasks"]

#------------
# TASK 1:Validaciones y manejo de errores
#------------


def category_exists(category_id):
    return any(c["id"] == category_id for c in data["categories"])

def is_title_duplicate(title, category_id):
    return any(t["title"] == title and t["category_id"] == category_id for t in data["tasks"])

#----Creación de tarea (POST /tasks) (Check!)

@app.route('/tasks', methods=['POST'])
def create_task():
    task = request.json
    
    if not task.get("title") or not task.get("category_id"):
        return jsonify({"error": "title y category_id son obligatorios"}), 400
    
    if len(task["title"]) < 3 or len(task["title"]) > 100:
        return jsonify({"error": "El título debe tener entre 3 y 100 caracteres"}), 400
    
    if not isinstance(task.get("completed"), bool):
        return jsonify({"error": "completed debe ser un booleano"}), 400
    
    if not category_exists(task["category_id"]):
        return jsonify({"error": "category_id no existe"}), 400
    
    if is_title_duplicate(task["title"], task["category_id"]):
        return jsonify({"error": "El título ya existe en esta categoría"}), 400
    
    task["id"] = len(data["tasks"]) + 1
    data["tasks"].append(task)
    return jsonify(task), 201

#----Creación de categoría (POST /categories) (Check!)
@app.route('/categories', methods=['POST'])
def create_category():
    category = request.json
    
    if not category.get("name"):
        return jsonify({"error": "El nombre de la categoría es obligatorio"}), 400
    
    if any(c["name"].lower() == category["name"].lower() for c in data["categories"]):
        return jsonify({"error": "El nombre de la categoría ya existe"}), 400
    
    category["id"] = len(data["categories"]) + 1
    data["categories"].append(category)
    return jsonify(category), 201

#----Actualización completa de una tarea (PUT /tasks/{task_id}) (Check!)
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    
    updated_task = request.json
    
    if not updated_task.get("title") or not updated_task.get("category_id") or "completed" not in updated_task:
        return jsonify({"error": "title, category_id y completed son obligatorios"}), 400
    
    if len(updated_task["title"]) < 3 or len(updated_task["title"]) > 100:
        return jsonify({"error": "El título debe tener entre 3 y 100 caracteres"}), 400
    
    if not isinstance(updated_task["completed"], bool):
        return jsonify({"error": "completed debe ser un booleano"}), 400
    
    if not category_exists(updated_task["category_id"]):
        return jsonify({"error": "category_id no existe"}), 400
    
    if is_title_duplicate(updated_task["title"], updated_task["category_id"]):
        return jsonify({"error": "El título ya existe en esta categoría"}), 400
    
    task.update(updated_task)
    save_data()
    return jsonify(task), 200

#----Actualización completa de una categoría (PUT /categories/{category_id}) (Check!)
@app.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = next((c for c in data["categories"] if c["id"] == category_id), None)
    if category is None:
        return jsonify({"error": "Categoría no encontrada"}), 404
    
    new_data = request.json
    if not new_data.get("name"):
        return jsonify({"error": "El nombre de la categoría es obligatorio"}), 400
    
    if any(c["name"].lower() == new_data["name"].lower() and c["id"] != category_id for c in data["categories"]):
        return jsonify({"error": "El nombre de la categoría ya existe"}), 400
    
    category["name"] = new_data["name"]
    save_data()
    return jsonify(category), 200


#----Eliminación de tarea (DELETE /tasks/{task_id}) (Check!)
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    
    data["tasks"].remove(task)
    save_data()
    return jsonify({"message": "Tarea eliminada"}), 200


#----Eliminación de categoría (DELETE /categories/{category_id}) (Check!)
@app.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = next((c for c in data["categories"] if c["id"] == category_id), None)
    if category is None:
        return jsonify({"error": "Categoría no encontrada"}), 404
    
    if any(t["category_id"] == category_id for t in data["tasks"]):
        return jsonify({"error": "No se puede eliminar una categoría con tareas asociadas"}), 400
    
    data["categories"].remove(category)
    save_data()
    return jsonify({"message": "Categoría eliminada"}), 200


# Obtener todas las categorías
@app.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(categories)


# Obtener todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

# Actualización parcial de una tarea
@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def patch_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task is None:
        abort(404, description="Tarea no encontrada")
    data = request.json
    task.update({
        key: data[key] for key in data if key in task
    })
    save_data()
    return jsonify(task)


if __name__ == '__main__':
    app.run(debug=True)
