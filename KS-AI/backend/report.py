from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt
import random, os

def generate_chart(filename="chart.png"):
    prices = [60000]
    for _ in range(20):
        prices.append(prices[-1] + random.randint(-500, 700))
    plt.figure(figsize=(6, 3))
    plt.plot(prices, label="BTC Price")
    plt.axhline(prices[-1]*1.05, color="green", linestyle="--", label="Target +5%")
    plt.axhline(prices[-1]*0.97, color="red", linestyle="--", label="Stop Loss")
    plt.legend()
    plt.title("BTC Trend & Targets")
    plt.savefig(filename)
    plt.close()
    return filename

def create_crypto_report(filename, title, analysis, logo_path="frontend/public/KSAI logo.png"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Logo + Title
    try:
        c.drawImage(logo_path, 40, height-100, width=80, height=80, preserveAspectRatio=True)
    except:
        pass
    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, height-60, title)

    # Analysis Text
    c.setFont("Helvetica", 12)
    text = c.beginText(40, height-140)
    for line in analysis.split("\n"):
        text.textLine(line)
    c.drawText(text)

    # Chart
    chart_file = generate_chart()
    try:
        c.drawImage(chart_file, 40, 200, width=500, height=200)
    except:
        pass

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(40, 30, f"© {datetime.now().year} KS-AI | All rights reserved.")

    c.save()
    if os.path.exists(chart_file):
        os.remove(chart_file)
    return filename
