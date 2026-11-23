"""Member 3: Simple suggested price calculator."""
def suggested_price(material_cost, labour_cost, other_cost, margin_percent):
    total_cost = material_cost + labour_cost + other_cost
    return total_cost, total_cost * (1 + margin_percent / 100)

def main():
    print("SakhiMart – Handmade Product Pricing Assistant")
    try:
        material = float(input("Raw material cost (₹): "))
        labour = float(input("Labour cost (₹): "))
        other = float(input("Other costs (₹): "))
        margin = float(input("Desired markup (%): "))
        if min(material, labour, other, margin) < 0:
            raise ValueError("Values cannot be negative.")
        cost, price = suggested_price(material, labour, other, margin)
        print(f"Total estimated cost: ₹{cost:.2f}")
        print(f"Suggested selling price: ₹{price:.2f}")
        print("Note: This is a cost-plus estimate; compare with local market prices.")
    except ValueError as error:
        print("Invalid input:", error)

if __name__ == "__main__":
    main()
