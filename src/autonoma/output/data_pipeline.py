import os
from data_loader import load_csv, load_json, save_csv, save_json
from data_processor import data_processing, analyze_data, transform_data
from data_visualization import visualize_data, plot_analysis
from utils import generate_random_data

def run_pipeline(input_file_path: str, output_file_path: str, file_type: str):
    # Load data
    if file_type == 'csv':
        data = load_csv(input_file_path)
    elif file_type == 'json':
        data = load_json(input_file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    # Process data
    processed_data = data_processing(data)
    analysis_result = analyze_data(processed_data)
    transformed_data = transform_data(processed_data)

    # Visualize data
    visualize_data(processed_data)
    plot_analysis(analysis_result)

    # Save results
    if file_type == 'csv':
        save_csv(transformed_data, output_file_path)
    elif file_type == 'json':
        save_json(transformed_data, output_file_path)

if __name__ == "__main__":
    # Example usage
    input_path = 'data/input.csv'
    output_path = 'data/output.csv'
    run_pipeline(input_path, output_path, 'csv')
