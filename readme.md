## Installation and Running the Application

1. **Clone the repository**:
    ```bash
    git clone https://github.com/SingleView11/DataSEA
    cd DataSEA
    ```

2. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application**:
    ```bash
    python app.py
    ```

4. **Input dataset name**:  
   After starting `app.py`, the application will prompt you to input the dataset name and optionally additional information. Type the dataset name in the CLI.

5. **Wait for processing**:  
   The system will process the request for 3 - 10 minutes.

6. **Check the results**:  
   Once completed, the results will be stored as a zipped file in the `experiment_results` folder. It zips all files in the `draft` folder, which contains the output.

7. **Rerun the application**:  
   If you rerun the application, it will delete the existing `draft` folder before generating new results.
