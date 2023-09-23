import os
from flask import Flask, request, render_template, send_file
from gradio_client import Client
import csv

app = Flask(__name__)

# Specify the URL of the Gradio server where the model is hosted.
client = Client("https://artificialguybr-qwen-vl.hf.space/")

# Get the absolute path to the directory where this Python script is located.
script_directory = os.path.dirname(os.path.abspath(__file__))

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    uploaded_image = None

    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file.filename != "":
            # Generate a unique temporary file path in the script directory.
            temp_file_path = os.path.join(script_directory, "temp_image.jpg")  # Change the extension as needed

            # Save the uploaded file temporarily.
            uploaded_file.save(temp_file_path)

            # Verify that the file exists.
            if os.path.isfile(temp_file_path):
                # Pass the path of the uploaded image to the template.
                uploaded_image = temp_file_path

                # Specify the explanation prompt.
                prompt = "give me the following details from it 1)Bank name 2) ifsc code 3)account number 4)amount 5)name of the receiver 6) check number and date .The answers are "
                choice = ""

                # Initialize result as empty to enter the loop.
                result = ""

                while not result:
                    # Send a prediction request to the server.
                    result = client.predict(
                        temp_file_path,
                        prompt,
                        choice,
                        api_name="/predict"
                    )

                # Check if the result is not empty.
                if result:
                    # Define a CSV file name to save the data.
                    csv_file = os.path.join(script_directory, "output.csv")

                    # Store the result as a single entry in the CSV.
                    with open(csv_file, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(["Details"])
                        writer.writerow([result[1].strip()])

                    result_text = "Data has been stored as CSV: " + csv_file
                else:
                    result_text = "Result is empty."

                # Delete the temporary file.
                # Comment out this line to retain the temporary image file.
                os.remove(temp_file_path)

                return render_template("index.html", result=result_text, uploaded_image=uploaded_image, csv_file=csv_file)

    return render_template("index.html", result=None, uploaded_image=uploaded_image)

@app.route("/csv")
def csv_output():
    # Define the path to the CSV file.
    csv_file = os.path.join(script_directory, "output.csv")

    # Check if the CSV file exists.
    if os.path.isfile(csv_file):
        return send_file(csv_file, as_attachment=True, download_name="output.csv")
    else:
        return "CSV file not found."

if __name__ == "__main__":
    app.run(debug=True)


