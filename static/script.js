document.addEventListener('DOMContentLoaded', () => {
            // DOM elements
            const fileInput = document.getElementById('fileInput');
            const browseBtn = document.getElementById('browseBtn');
            const uploadArea = document.getElementById('uploadArea');
            const previewContainer = document.getElementById('previewContainer');
            const previewImage = document.getElementById('previewImage');
            const removeBtn = document.getElementById('removeBtn');
            const processBtn = document.getElementById('processBtn');
            const statusMessage = document.getElementById('statusMessage');
            const progressBar = document.getElementById('progressBar');
            const progressBarInner = progressBar.querySelector('.progress-bar');
            const fileInfo = document.getElementById('fileInfo');
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const clearBtn = document.getElementById('clearBtn');
            const convertNumbers = document.getElementById('convertNumbers');
            const convertPercentages = document.getElementById('convertPercentages');
            
            // Event listeners
            //browseBtn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', handleFileSelect);
            uploadArea.addEventListener('dragover', handleDragOver);
            uploadArea.addEventListener('dragleave', handleDragLeave);
            uploadArea.addEventListener('drop', handleDrop);
            removeBtn.addEventListener('click', resetForm);
            processBtn.addEventListener('click', processImage);
            clearBtn.addEventListener('click', resetForm);
            uploadArea.addEventListener('click', () => fileInput.click())
            
            // Handle file selection
            function handleFileSelect(e) {
                const file = e.target.files[0];
                if (validateFile(file)) {
                    previewFile(file);
                    updateFileInfo(file);
                }
            }
            
            // Drag and drop handlers
            function handleDragOver(e) {
                e.preventDefault();
                uploadArea.style.borderColor = '#0d6efd';
                uploadArea.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
            }
            
            function handleDragLeave() {
                uploadArea.style.borderColor = '';
                uploadArea.style.backgroundColor = '';
            }
            
            function handleDrop(e) {
                e.preventDefault();
                handleDragLeave();
                
                if (e.dataTransfer.files.length) {
                    const file = e.dataTransfer.files[0];

                    fileInput.files = e.dataTransfer.files

                    if (validateFile(file)) {
                        previewFile(file);
                        updateFileInfo(file);
                    }
                }
            }
            
            // Validate file
            function validateFile(file) {
                if (!file) {
                    showStatus('No file selected', 'error');
                    return false;
                }
                
                const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
                if (!validTypes.includes(file.type)) {
                    showStatus('Invalid file type. Please upload a PNG, JPG, or JPEG image.', 'error');
                    return false;
                }
                
                // Check file size (max 4MB)
                if (file.size > 4 * 1024 * 1024) {
                    showStatus('File size exceeds 4MB limit. Please choose a smaller file.', 'error');
                    return false;
                }
                
                return true;
            }
            
            // Preview file
            function previewFile(file) {
                const reader = new FileReader();
                
                reader.onload = (e) => {
                    previewImage.src = e.target.result;
                    previewContainer.style.display = 'block';
                };
                
                reader.readAsDataURL(file);
            }
            
            // Update file info
            function updateFileInfo(file) {
                fileName.textContent = file.name;
                fileSize.textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
                fileInfo.classList.remove('d-none');
            }
            
            // Reset form
            function resetForm() {
                fileInput.value = '';
                previewImage.src = '';
                previewContainer.style.display = 'none';
                fileInfo.classList.add('d-none');
                hideStatus();
                progressBar.style.display = 'none';
                progressBarInner.style.width = '0%';
            }
            
            // Process image with error handling
            function processImage() {
                if (!fileInput.files.length) {
                    showStatus('Please upload an image.', 'error');
                    return;
                }
                
                // Get selected options
                const convertNumbersValue = convertNumbers.checked;
                const convertPercentagesValue = convertPercentages.checked;
                
                // Show processing status
                showStatus('Processing image...', 'processing');
                progressBar.style.display = 'block';

                // Actual implementation would look like this:
                const formData = new FormData();
                formData.append('image', fileInput.files[0]);
                formData.append('convertNumbers', convertNumbersValue);
                formData.append('convertPercentages', convertPercentagesValue);
                
                fetch('/process_image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status} ${response.statusText}`);
                    }
                    return response.blob();
                })
                .then(blob => {
                    // Get filename from Content-Disposition header if available
                    let filename = `processed_${fileName.textContent || "output"}.xlsx`;
                    
                    // Download the file automatically
                    download(blob, filename);
                    
                    showStatus('Image processed successfully!', 'success');
                    progressBar.style.display = 'none';
                })
                .catch(error => {
                    console.error('Error:', error);
                    showStatus(`Error processing image: ${error.message}`, 'error');
                    progressBar.style.display = 'none';
                });
                
            }
            
            // Show status message
            function showStatus(message, type) {
                statusMessage.textContent = message;
                statusMessage.className = 'status-message';
                statusMessage.classList.add(`status-${type}`);
                statusMessage.style.display = 'block';
            }
            
            // Hide status message
            function hideStatus() {
                statusMessage.style.display = 'none';
            }
        });