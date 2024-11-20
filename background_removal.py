import os
import logging
import tkinter as tk
from tkinter import (filedialog, messagebox, ttk, 
                     PhotoImage, Canvas, Scrollbar)
import cv2
import numpy as np
from PIL import Image, ImageTk

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='background_remover.log'
)

class AdvancedBackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Background Remover")
        
        # Configure window
        self.root.geometry("1200x900")
        self.root.configure(bg='#2c3e50')
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', 
            background='#3498db', 
            foreground='white', 
            font=('Arial', 10, 'bold')
        )
        self.style.configure('TLabel', 
            background='#2c3e50', 
            foreground='white', 
            font=('Arial', 12)
        )
        
        # Main frame
        self.main_frame = tk.Frame(root, bg='#2c3e50')
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Create sections
        self.create_input_section()
        self.create_preview_section()
        self.create_options_section()
        
        # Image storage
        self.original_image = None
        self.processed_image = None
    
    def create_input_section(self):
        input_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        input_frame.pack(fill=tk.X, pady=10)
        
        # Input button
        self.input_btn = ttk.Button(
            input_frame, 
            text="Select Input Image", 
            command=self.load_input_image
        )
        self.input_btn.pack(side=tk.LEFT, padx=10)
        
        # Input path display
        self.input_path_var = tk.StringVar()
        self.input_path_label = ttk.Label(
            input_frame, 
            textvariable=self.input_path_var, 
            width=50
        )
        self.input_path_label.pack(side=tk.LEFT, padx=10)
    
    def create_preview_section(self):
        preview_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        preview_left = tk.Frame(preview_frame, bg='#2c3e50')
        preview_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        preview_right = tk.Frame(preview_frame, bg='#2c3e50')
        preview_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Original image canvas
        tk.Label(preview_left, text="Original Image", 
                 bg='#2c3e50', fg='white', font=('Arial', 12)).pack()
        self.original_canvas = tk.Canvas(
            preview_left, 
            bg='#34495e', 
            highlightthickness=0
        )
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Processed image canvas
        tk.Label(preview_right, text="Processed Image", 
                 bg='#2c3e50', fg='white', font=('Arial', 12)).pack()
        self.processed_canvas = tk.Canvas(
            preview_right, 
            bg='#34495e', 
            highlightthickness=0
        )
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)
    
    def create_options_section(self):
        options_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        options_frame.pack(fill=tk.X, pady=10)
        
        # Processing options
        self.debug_var = tk.BooleanVar(value=False)
        debug_check = ttk.Checkbutton(
            options_frame, 
            text="Debug Mode", 
            variable=self.debug_var,
            style='TCheckbutton'
        )
        debug_check.pack(side=tk.LEFT, padx=10)
        
        # Algorithm selection
        self.algorithm_var = tk.StringVar(value="grabcut")
        algorithm_label = ttk.Label(options_frame, text="Algorithm:")
        algorithm_label.pack(side=tk.LEFT, padx=(10, 5))
        
        algorithm_dropdown = ttk.Combobox(
            options_frame, 
            textvariable=self.algorithm_var,
            values=["grabcut", "kmeans", "color_based"],
            state="readonly",
            width=15
        )
        algorithm_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        
        # Process and save buttons
        self.process_btn = ttk.Button(
            options_frame, 
            text="Process Image", 
            command=self.process_image
        )
        self.process_btn.pack(side=tk.LEFT, padx=10)
        
        self.save_btn = ttk.Button(
            options_frame, 
            text="Save Processed Image", 
            command=self.save_processed_image
        )
        self.save_btn.pack(side=tk.LEFT, padx=10)
    
    def load_input_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.input_path_var.set(file_path)
        
        try:
            self.original_image = cv2.imread(file_path)
            
            image_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            
            image_pil = self.resize_image(image_pil, 400, 400)
            
            photo = ImageTk.PhotoImage(image_pil)
            
            self.original_canvas.delete("all")
            self.original_canvas.create_image(
                self.original_canvas.winfo_width() // 2, 
                self.original_canvas.winfo_height() // 2, 
                image=photo, 
                anchor=tk.CENTER
            )
            self.original_canvas.image = photo
            
            logging.info(f"Loaded image: {file_path}")
            
        except Exception as e:
            logging.error(f"Image loading error: {e}")
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
    
    def resize_image(self, image, max_width, max_height):
        image.thumbnail((max_width, max_height), Image.LANCZOS)
        return image
    
    def process_image(self):
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please select an input image first.")
            return
        
        output_path = 'temp_processed_image.png'
        
        try:
            self.process_background_removal(output_path)
            
            processed_image = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            
            processed_image_rgb = cv2.cvtColor(processed_image[:,:,:3], cv2.COLOR_BGR2RGB)
            
            image_pil = Image.fromarray(processed_image_rgb)
            
            image_pil = self.resize_image(image_pil, 400, 400)
            
            photo = ImageTk.PhotoImage(image_pil)
            
            self.processed_canvas.delete("all")
            self.processed_canvas.create_image(
                self.processed_canvas.winfo_width() // 2, 
                self.processed_canvas.winfo_height() // 2, 
                image=photo, 
                anchor=tk.CENTER
            )
            self.processed_canvas.image = photo
            
            logging.info(f"Image processed with {self.algorithm_var.get()} algorithm")
            messagebox.showinfo("Success", "Image processed successfully!")
        
        except Exception as e:
            logging.error(f"Image processing failed: {e}")
            messagebox.showerror("Error", f"Image processing failed: {str(e)}")
    
    def process_background_removal(self, output_path):
        original_image = cv2.imread(self.input_path_var.get())
        
        # Select algorithm based on dropdown
        if self.algorithm_var.get() == "grabcut":
            final_mask = self._grabcut_segmentation(original_image)
        elif self.algorithm_var.get() == "kmeans":
            final_mask = self._kmeans_segmentation(original_image)
        else:
            final_mask = self._color_based_segmentation(original_image)
        
        # Create 4-channel output image
        result = np.zeros(original_image.shape[:2] + (4,), dtype=np.uint8)
        result[:,:,:3] = original_image
        result[:,:,3] = final_mask * 255
        
        # Debug visualization
        if self.debug_var.get():
            masked_image = original_image.copy()
            masked_image[final_mask == 0] = [0, 0, 255]
            cv2.imwrite('debug_background_removal.png', masked_image)
        
        # Save the output image
        cv2.imwrite(output_path, result)
    
    def save_processed_image(self):
        if not os.path.exists('temp_processed_image.png'):
            messagebox.showwarning("Warning", "No processed image to save.")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy('temp_processed_image.png', save_path)
                logging.info(f"Image saved to {save_path}")
                messagebox.showinfo("Success", f"Image saved to {save_path}")
            except Exception as e:
                logging.error(f"Image save failed: {e}")
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
    
    def _grabcut_segmentation(self, image):
        mask = np.zeros(image.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        rect = (50, 50, image.shape[1] - 100, image.shape[0] - 100)
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        mask_final = np.where(
            (mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1
        ).astype('uint8')
        
        return mask_final
    
    def _kmeans_segmentation(self, image):
        # Convert image to 2D array of pixels
        pixels = image.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # Define criteria and apply k-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 2
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Reshape labels to original image dimension
        labels = labels.reshape(image.shape[:2])
        
        # Create binary mask (assume 0 is background)
        mask = (labels == 0).astype(np.uint8)
        return mask
    
    def _color_based_segmentation(self, image):
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define range for background colors
        lower_background = np.array([0, 0, 0])
        upper_background = np.array([180, 50, 50])
        
        # Threshold the HSV image to get only background colors
        mask = cv2.inRange(hsv, lower_background, upper_background)
        
        # Morphological operations to clean mask
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Invert mask (foreground becomes white)
        mask = cv2.bitwise_not(mask)
        return mask

def main():
    root = tk.Tk()
    app = AdvancedBackgroundRemoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()