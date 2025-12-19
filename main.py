import tkinter as tk


def main() -> None:
    root = tk.Tk()
    root.title("PONG")
    root.geometry("800x500")
    root.configure(bg="black")

    canvas = tk.Canvas(root, width=800, height=500, bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_text(
        400,
        250,
        text="PONG",
        fill="white",
        font=("Helvetica", 48, "bold"),
    )

    root.mainloop()


if __name__ == "__main__":
    main()
