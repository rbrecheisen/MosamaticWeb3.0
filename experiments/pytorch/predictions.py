import torch
import numpy as np
import matplotlib.pyplot as plt
import h5py
import argparse
import os
import json
import cv2  
from models import UNet
import utils

# Define the colormap
color_map = {
    0: [0, 0, 0],        # Background - black
    1: [255, 0, 0],      # Muscle - red
    2: [255, 255, 0],    # Visceral adipose tissue - yellow
    3: [0, 255, 255]     # Subcutaneous adipose tissue - cyan
}

# Function to apply color map
def apply_color_map(prediction, color_map):
    height, width = prediction.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    
    for label, color in color_map.items():
        mask = (prediction == label)
        rgb_image[mask] = color

    return rgb_image

def main(data_path, output_dir):
    try:
        # Load parameters
        param_path = os.getcwd() + '/params.json'
        params = utils.Params(param_path)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load model
        model_path = '/mnt/localscratch/maastro/Gokul/Development/pytorch/logs/gradient_tape/20240525-112355/saved_models/model_full_100000.pth'
        model = torch.load(model_path, map_location=device)
        model.to(device)
        model.eval()

        # Load dataset 
        print(f"Loading dataset from {data_path}")
        original_images, images, labels, patient_ids = utils.load_dataset_contour_prediction(data_path, params, norm=True)

        num_patients = images.shape[2]
        print(f"Total number of patients: {num_patients}")
        
        # Create a directory to save the predictions
        os.makedirs(output_dir, exist_ok=True)  

        # Process each image
        for i in range(num_patients):
            print(f"Processing patient ID: {patient_ids[i]}")

            original_ct = original_images[:, :, i]  # Original CT image
            ct = utils.normalize(images[:, :, i], 'True', params.min_bound, params.max_bound)

            # Resize image to expected dimensions and convert to tensors
            target_shape = (512, 512)  
            original_ct_resized = cv2.resize(original_ct, target_shape, interpolation=cv2.INTER_LINEAR)
            ct_resized = cv2.resize(ct, target_shape, interpolation=cv2.INTER_LINEAR)
            ct_resized_tensor = torch.tensor(ct_resized, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)

            # Predict segmentation
            with torch.no_grad():
                pred = model(ct_resized_tensor).cpu().numpy()
            pred_squeeze = np.squeeze(pred)

            # Convert predicted labels to integer classes
            pred_max = np.argmax(pred_squeeze, axis=0)

            # Apply the color map to the predicted segmentation
            pred_rgb = apply_color_map(pred_max, color_map)

            # Plot the results (single row with original, predicted, and ground truth)
            fig, axs = plt.subplots(1, 3, figsize=(15, 5))  # Single row, 3 columns

            # Plot original, predicted segmentation, and ground truth
            axs[0].imshow(original_ct_resized, cmap='gray')  # Original CT image
            axs[0].set_title('Original CT Image')

            axs[1].imshow(labels[:, :, i], cmap='gray')  # Ground truth
            axs[1].set_title('Ground Truth')

            axs[2].imshow(pred_rgb)  # Predicted segmentation with color map
            axs[2].set_title('Predicted Segmentation')

            # Adjust layout for proper alignment and spacing
            plt.tight_layout(pad=2.0)

            # Save the plot as an image file for each patient
            output_path = os.path.join(output_dir, f'predictions_patient_{i + 1}.png')
            plt.savefig(output_path)
            plt.close(fig)  # Close the figure to free memory
            print(f"Predictions for patient {patient_ids[i]} saved as '{output_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, help='Path to the new dataset (HDF5 file).')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save the predictions.')
    args = parser.parse_args()
    main(args.dataset, args.output_dir)
