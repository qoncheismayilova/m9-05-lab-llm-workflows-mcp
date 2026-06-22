import ollama
import json

# Orders load
with open("orders.json", "r") as f:
    orders = json.load(f)

# Memory
messages = []

# Step limit
STEP_LIMIT = 5


# Tool 1
def lookup_order(order_id):
    return orders.get(order_id, {"error": "Order not found"})


# Tool 2
def calculate(expression):
    try:
        return eval(expression)
    except:
        return "Calculation error"


def run_loop(user_input):
    messages.append({
        "role": "user",
        "content": user_input
    })

    for step in range(STEP_LIMIT):
        print(f"\n===== STEP {step+1} =====")

        response = ollama.chat(
            model="llama3.2",
            messages=messages
        )

        output = response["message"]["content"]
        print("MODEL OUTPUT:")
        print(output)

        try:
            tool_call = json.loads(output)

            tool_name = tool_call["tool"]
            args = tool_call["args"]

            print("TOOL REQUESTED:", tool_name)

            if tool_name == "lookup_order":
                result = lookup_order(args["order_id"])

            elif tool_name == "calculate":
                result = calculate(args["expression"])

            else:
                result = "Unknown tool"

            print("TOOL RESULT:", result)

            # save model tool call
            messages.append({
                "role": "assistant",
                "content": output
            })

            # save tool result
            messages.append({
                "role": "user",
                "content": f"Tool result: {result}"
            })

        except:
            print("FINAL ANSWER:", output)

            messages.append({
                "role": "assistant",
                "content": output
            })

            return

    print("Couldn't finish in time.")


# TURN 1
run_loop("""
You MUST NEVER calculate by yourself.
You MUST use tools.

Rules:
1. If user asks order price → use lookup_order.
2. If user asks multiplication → use calculate.
3. Never invent numbers.
4. Return only JSON.

lookup_order example:
{"tool":"lookup_order","args":{"order_id":"A1001"}}

calculate example:
{"tool":"calculate","args":{"expression":"3*1200"}}

Question: What did order A1001 cost?
""")

# TURN 2
run_loop("And what about three of them?")