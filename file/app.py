from flask import Flask, request, jsonify
from flask_cors import CORS
import z3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    grid = data['grid']
    size = len(grid)
    
    # Debug: Print the received grid
    print("Received grid:", grid)
    
    try:
        x = [[z3.Int(f'x_{i}_{j}') for j in range(size)] for i in range(size)]

        cells_c = [z3.And(x[i][j] >= 1, x[i][j] <= size) for i in range(size) for j in range(size)]

        rows_c = [z3.Distinct(x[i]) for i in range(size)]

        cols_c = [z3.Distinct([x[i][j] for i in range(size)]) for j in range(size)]

        sqrt_size = int(size**0.5)
        sq_c = [z3.Distinct([x[i + k][j + l] for k in range(sqrt_size) for l in range(sqrt_size)])
                for i in range(0, size, sqrt_size) for j in range(0, size, sqrt_size)]

        instance = [z3.If(grid[i][j] == 0, True, x[i][j] == grid[i][j])
                    for i in range(size) for j in range(size)]

        s = z3.Solver()
        s.add(cells_c + rows_c + cols_c + sq_c + instance)

        if s.check() == z3.sat:
            m = s.model()
            solution = [[m.evaluate(x[i][j]).as_long() for j in range(size)] for i in range(size)]
            return jsonify(solution)
        else:
            return 'No solution exists', 400
    except Exception as e:
        print("Exception:", e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
