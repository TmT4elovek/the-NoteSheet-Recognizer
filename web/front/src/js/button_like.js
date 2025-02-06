import React, { useState } from 'react';

const PhotoUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      alert("Пожалуйста, выберите файл для загрузки.");
      return;
    }

    const formData = new FormData();
    formData.append('photo', selectedFile);

    try {
      const response = await fetch('YOUR_UPLOAD_URL_HERE', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert("Фотография успешно загружена!");
      } else {
        alert("Ошибка при загрузке фотографии.");
      }
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Произошла ошибка при загрузке фотографии.");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button type="submit">Отправить фотографию</button>
    </form>
  );
};



const domContainer = document.querySelector('#like_button_container');
const root = ReactDOM.createRoot(domContainer);
root.render(e(LikeButton));
export default PhotoUpload;
