

def make_calculator_tool():
    def calculate(expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Lỗi tính toán: {e}"

    return {
        "name": "calculator",
        "description": "Tính toán biểu thức số học. Input là một biểu thức như '100 * 1.05' hoặc '(200 + 50) / 3'.",
        "func": calculate,
    }

TOOLS = [make_calculator_tool()]

