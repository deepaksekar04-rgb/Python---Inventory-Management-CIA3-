import os

STOCK_FILE = "stock.txt"
PURCHASE_FILE = "purchases.txt"

# List of tuples - Default products
DEFAULT_PRODUCTS = [
    ("P01", "Steel Rod",        120, 250.0, "MetalCorp",    30,  100),
    ("P02", "Aluminium Sheet",  80,  180.0, "AlumTrade",    20,  50),
    ("P03", "Copper Wire",      15,  320.0, "WirePlus",     20,  60),
    ("P04", "Bearing 6205",     200, 95.0,  "SKF Dist.",    50,  80),
    ("P05", "Hydraulic Oil",    18,  410.0, "LubriCo",      25,  40),
    ("P06", "Drill Bit Set",    40,  560.0, "ToolMart",     10,  20),
    ("P07", "Safety Gloves",    10,  75.0,  "SafetyPro",    20,  50),
    ("P08", "Welding Rod",      300, 135.0, "WeldSupply",   80,  150),
    ("P09", "PVC Pipe 2in",     55,  60.0,  "PipeLine Co.", 15,  30),
    ("P10", "Grease Cartridge", 18,  220.0, "LubriCo",      25,  30),
    ("P11", "Hex Bolt M12",     500, 12.0,  "FastenerHub",  100, 300),
    ("P12", "Lathe Tool Bit",   25,  480.0, "CutTech",      10,  20),
    ("P13", "Rubber Gasket",    8,   45.0,  "SealMaster",   20,  50),
    ("P14", "Paint Grey 1L",    30,  310.0, "CoatPro",      10,  25),
    ("P15", "Cutting Disc",     60,  85.0,  "ToolMart",     20,  40),
]

# ── File Operations ────────────────────────────────────────────────────────────

def write_inventory(inv):
    with open(STOCK_FILE, "w") as f:
        for pid, p in inv.items():
            f.write(f"{pid}|{p['name']}|{p['qty']}|{p['price']}|{p['dealer']}|{p['alert']}|{p['order_qty']}\n")

def read_inventory():
    inv = {}
    if not os.path.exists(STOCK_FILE):
        return inv
    with open(STOCK_FILE, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) != 7:
                continue
            pid, name, qty, price, dealer, alert, oqty = parts
            inv[pid] = {"name": name, "qty": int(qty), "price": float(price),
                        "dealer": dealer, "alert": int(alert), "order_qty": int(oqty)}
    return inv

def write_orders(orders):
    with open(PURCHASE_FILE, "w") as f:
        for o in orders:
            f.write(f"{o['oid']}|{o['pid']}|{o['name']}|{o['dealer']}|{o['qty']}|{o['status']}\n")

def read_orders():
    orders = []
    if not os.path.exists(PURCHASE_FILE):
        return orders
    with open(PURCHASE_FILE, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) != 6:
                continue
            oid, pid, name, dealer, qty, status = parts
            orders.append({"oid": oid, "pid": pid, "name": name,
                           "dealer": dealer, "qty": int(qty), "status": status})
    return orders

# ── Load Defaults ──────────────────────────────────────────────────────────────

def load_defaults():
    inv = {}
    for t in DEFAULT_PRODUCTS:
        pid, name, qty, price, dealer, alert, oqty = t
        inv[pid] = {"name": name, "qty": qty, "price": price,
                    "dealer": dealer, "alert": alert, "order_qty": oqty}
    write_inventory(inv)
    return inv

# ── Display ────────────────────────────────────────────────────────────────────

def show_inventory(inv):
    print(f"\n{'ID':<6}{'Name':<18}{'Qty':<7}{'Price':<9}{'Dealer':<16}{'Alert':<7}Status")
    print("-" * 68)
    for pid, p in inv.items():
        s = "OUT" if p['qty'] == 0 else ("LOW" if p['qty'] <= p['alert'] else "OK")
        print(f"{pid:<6}{p['name']:<18}{p['qty']:<7}Rs.{p['price']:<6}{p['dealer']:<16}{p['alert']:<7}{s}")

# ── Alerts & Auto-Order ────────────────────────────────────────────────────────

def check_alerts(inv, orders):
    pending_pids = {o['pid'] for o in orders if o['status'] == "Pending"}  # set
    print("\n---- STOCK ALERTS ----")
    found = False
    for pid, p in inv.items():
        if p['qty'] <= p['alert']:
            found = True
            tag = "OUT OF STOCK" if p['qty'] == 0 else f"LOW - {p['qty']} left"
            print(f"!  {p['name']} ({pid}) : {tag}")
            if pid not in pending_pids:
                c = input(f"   Order {p['order_qty']} units from {p['dealer']}? (y/n): ")
                if c.lower() == 'y':
                    oid = f"ORD{len(orders)+1:03d}"
                    orders.append({"oid": oid, "pid": pid, "name": p['name'],
                                   "dealer": p['dealer'], "qty": p['order_qty'], "status": "Pending"})
                    write_orders(orders)
                    pending_pids.add(pid)
                    print(f"   Order {oid} placed!")
            else:
                print(f"   Order already pending.")
    if not found:
        print("All stocks OK.")
    print("----------------------")
    return orders

# ── Add Product ────────────────────────────────────────────────────────────────

def add_product(inv):
    pid = input("Product ID: ").upper()
    if pid in inv:
        print("ID exists!"); return inv
    inv[pid] = {
        "name":      input("Name: "),
        "qty":       int(input("Qty: ")),
        "price":     float(input("Price: ")),
        "dealer":    input("Dealer: "),
        "alert":     int(input("Alert at qty: ")),
        "order_qty": int(input("Auto-order qty: "))
    }
    write_inventory(inv)
    print("Added!")
    return inv

# ── Edit Product ───────────────────────────────────────────────────────────────

def edit_product(inv):
    pid = input("Product ID to edit: ").upper()
    if pid not in inv:
        print("Not found!"); return inv
    p = inv[pid]
    fields = [("name", str), ("qty", int), ("price", float),
              ("dealer", str), ("alert", int), ("order_qty", int)]
    for key, dtype in fields:
        val = input(f"{key} [{p[key]}]: ").strip()
        if val:
            p[key] = dtype(val)
    write_inventory(inv)
    print("Updated!")
    return inv

# ── Add Stock ──────────────────────────────────────────────────────────────────

def add_stock(inv):
    pid = input("Product ID: ").upper()
    if pid not in inv:
        print("Not found!"); return inv
    inv[pid]['qty'] += int(input(f"Units to add (current: {inv[pid]['qty']}): "))
    write_inventory(inv)
    print(f"New qty: {inv[pid]['qty']}")
    return inv

# ── Delete Product ─────────────────────────────────────────────────────────────

def delete_product(inv):
    pid = input("Product ID to delete: ").upper()
    if pid not in inv:
        print("Not found!"); return inv
    if input(f"Delete '{inv[pid]['name']}'? (y/n): ").lower() == 'y':
        del inv[pid]
        write_inventory(inv)
        print("Deleted!")
    return inv

# ── View Orders ────────────────────────────────────────────────────────────────

def view_orders(orders):
    if not orders:
        print("No orders."); return
    print(f"\n{'OID':<8}{'Product':<18}{'Qty':<6}{'Dealer':<16}Status")
    print("-" * 55)
    for o in orders:
        print(f"{o['oid']:<8}{o['name']:<18}{o['qty']:<6}{o['dealer']:<16}{o['status']}")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n=== MANUFACTURING INVENTORY SYSTEM ===")
    inv = read_inventory() or load_defaults()
    orders = read_orders()
    check_alerts(inv, orders)

    while True:
        print("\n1.View  2.Add Product  3.Edit Product  4.Add Stock  5.Delete  6.Alerts  7.Orders  8.Exit")
        c = input("Choice: ").strip()
        if   c == '1': show_inventory(inv)
        elif c == '2': inv = add_product(inv)
        elif c == '3': inv = edit_product(inv)
        elif c == '4': inv = add_stock(inv)
        elif c == '5': inv = delete_product(inv)
        elif c == '6': orders = check_alerts(inv, orders)
        elif c == '7': view_orders(orders)
        elif c == '8': print("Goodbye!"); break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()