'use client';

import { useState } from 'react';

export default function SearchForm({ onSearch }) {
  const [category, setCategory] = useState('');
  const [priceRange, setPriceRange] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    onSearch(category, priceRange);
  };

  return (
    <div className="flex justify-center bg-gray-100 mb-8">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-lg w-full max-w-lg flex flex-col space-y-6"
      >
        <label className="text-gray-600 font-medium text-center mb-1">Категория товара</label>
        <input
          type="text"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder="Введите название категории"
          className="p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
        />

        <label className="text-gray-600 font-medium text-center mb-1">Ценовой диапазон</label>
        <select
          value={priceRange}
          onChange={(e) => setPriceRange(e.target.value)}
          className="p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
        >
          <option value="">Неважно</option>
          <option value="low">Низкий (до 5000 руб.)</option>
          <option value="medium">Средний (5000 - 20000 руб.)</option>
          <option value="high">Высокий (более 20000 руб.)</option>
        </select>

        <button
          type="submit"
          className="p-4 bg-orange-500 text-white rounded-lg shadow-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-400 transition"
        >
          Подобрать подарок
        </button>
      </form>
    </div>
  );
}
