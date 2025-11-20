import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
from groq import Groq


# -----------------------------
#  Helper functions
# -----------------------------

def create_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY not found in environment variables."

    try:
        client = Groq(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Groq init error: {e}"


def calculate(a, b, op):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b
    elif op == "^":
        return a ** b
    elif op == "%":
        return (a / 100.0) * b
    else:
        raise ValueError("Invalid operator")


def ask_groq(prompt):
    client, err = create_groq_client()
    if err:
        return f"ERROR: {err}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {e}"


# -----------------------------
#  GUI Application
# -----------------------------

class SmartCalculatorGUI:
    def __init__(self, root):
        self.root = root
        root.title("Smart Calculator (Groq AI)")
        root.geometry("600x600")

        self.history = []

        # ------------------- Basic Calculator -------------------
        tk.Label(root, text="Basic Calculator", font=("Arial", 16, "bold")).pack()

        frame = tk.Frame(root)
        frame.pack()

        tk.Label(frame, text="Number 1").grid(row=0, column=0)
        tk.Label(frame, text="Number 2").grid(row=1, column=0)

        self.num1 = tk.Entry(frame)
        self.num2 = tk.Entry(frame)
        self.num1.grid(row=0, column=1)
        self.num2.grid(row=1, column=1)

        tk.Label(frame, text="Operation").grid(row=2, column=0)

        self.operation = tk.StringVar(value="+")
        tk.OptionMenu(frame, self.operation, "+", "-", "*", "/", "^", "%").grid(row=2, column=1)

        tk.Button(frame, text="Calculate", command=self.do_calculation).grid(row=3, column=0, columnspan=2)

        self.result_label = tk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack()

        # ------------------- AI Explanation -------------------
        tk.Label(root, text="AI Explanation (Groq)", font=("Arial", 16, "bold")).pack()

        self.explain_text = scrolledtext.ScrolledText(root, width=60, height=5)
        self.explain_text.pack()

        tk.Button(root, text="Explain Using AI", command=self.explain_last_calc).pack()

        # ------------------- Natural Language Calculator -------------------
        tk.Label(root, text="Natural Language Question", font=("Arial", 16, "bold")).pack()

        self.nl_input = tk.Entry(root, width=60)
        self.nl_input.pack()

        tk.Button(root, text="Ask AI", command=self.ask_natural_language).pack()

        self.ai_answer = scrolledtext.ScrolledText(root, width=60, height=6)
        self.ai_answer.pack()

        # ------------------- History -------------------
        tk.Label(root, text="History", font=("Arial", 16, "bold")).pack()

        self.history_box = scrolledtext.ScrolledText(root, width=60, height=6)
        self.history_box.pack()

    # ------------------- Functions -------------------

    def do_calculation(self):
        try:
            a = float(self.num1.get())
            b = float(self.num2.get())
            op = self.operation.get()

            result = calculate(a, b, op)
            expr = f"{a} {op} {b} = {result}"

            self.result_label.config(text=expr)

            self.history.insert(0, expr)
            self.update_history()

            self.explain_text.delete(1.0, tk.END)
            self.explain_text.insert(tk.END, f"Last calculation: {expr}")

        except ZeroDivisionError as e:
            messagebox.showerror("Error", str(e))
        except:
            messagebox.showerror("Error", "Invalid input")

    def explain_last_calc(self):
        text = self.explain_text.get(1.0, tk.END).strip()
        if "Last calculation:" not in text:
            messagebox.showwarning("Warning", "Perform a calculation first.")
            return

        expr = text.replace("Last calculation:", "").strip()

        prompt = f"Explain step by step how to compute {expr} in simple words."
        explanation = ask_groq(prompt)

        self.explain_text.delete(1.0, tk.END)
        self.explain_text.insert(tk.END, explanation)

    def ask_natural_language(self):
        question = self.nl_input.get().strip()
        if not question:
            return

        prompt = (
            "Solve the following math question, give the numeric answer "
            "and explain step-by-step in simple language:\n\n"
            f"{question}"
        )

        answer = ask_groq(prompt)

        self.ai_answer.delete(1.0, tk.END)
        self.ai_answer.insert(tk.END, answer)

    def update_history(self):
        self.history_box.delete(1.0, tk.END)
        for item in self.history[:10]:
            self.history_box.insert(tk.END, item + "\n")


# ------------------- Run App -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCalculatorGUI(root)
    root.mainloop()
