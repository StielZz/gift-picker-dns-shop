'use client';

import { useState } from 'react';
import SearchForm from './components/SearchForm';
import ProductList from './components/ProductList';

export default function Page() {
  const [products, setProducts] = useState([]);

  const handleSearch = async (category, priceRange) => {
    const response = await fetch(`/api/products?category=${category}&priceRange=${priceRange}`);
    const data = await response.json();
    setProducts(data);
  };

  return (
    <div className="container mx-auto p-6">
      <SearchForm onSearch={handleSearch} />
      <ProductList products={products} />
    </div>
  );
}