from fastapi import FastAPI

app = FastAPI()


@app.post("/calculate")
def calculate(a: float, b: float):
    return {"a": a, "b": b, "sum": a + b, "product": a * b}
