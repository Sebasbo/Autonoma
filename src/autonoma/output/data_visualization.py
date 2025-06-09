
import matplotlib.pyplot as plt
from data_processor import data_processing, analyze_data
from utils import generate_random_data

def visualize_data(data):
    try:
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=20)
        plt.title('Data Distribution')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.show()
    except Exception as e:
        print(f"An error occurred while visualizing data: {e}")

def plot_analysis(analysis):
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(analysis.keys(), analysis.values())
        plt.title('Data Analysis')
        plt.xlabel('Value')
        plt.ylabel('Count')
        plt.show()
    except Exception as e:
        print(f"An error occurred while plotting analysis: {e}")

def scatter_plot(x, y):
    try:
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y)
        plt.title('Scatter Plot')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.show()
    except Exception as e:
        print(f"An error occurred while creating scatter plot: {e}")

def main():
    try:
        random_data = generate_random_data(1000)
        processed_data = data_processing(random_data)
        analysis_result = analyze_data(processed_data)
        
        visualize_data(processed_data)
        plot_analysis(analysis_result)
        # Add example scatter plot
        if len(processed_data) > 1:
            scatter_plot(processed_data[:len(processed_data)//2], processed_data[len(processed_data)//2:])
    except Exception as e:
        print(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()
