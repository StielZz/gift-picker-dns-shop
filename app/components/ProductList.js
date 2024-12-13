export default function ProductList({ products }) {
  return (
    <div className="flex overflow-x-auto space-x-4 p-4">
      {products.length > 0 ? (
        products.map((product) => (
          <div
            key={product.id}
            className="p-6 border rounded-lg shadow-md bg-white flex-none w-64 h-80 flex flex-col items-center justify-center"
          >
            <h3 className="text-xl font-semibold text-gray-800 text-center">
              {product.title}
            </h3>
            <p className="text-lg text-gray-600 mt-2 text-center">
              Цена: {product.price} руб.
            </p>
          </div>
        ))
      ) : (
        <div className="flex items-center justify-center w-full h-80">
          <p className="text-center text-gray-500">Товары не найдены</p>
        </div>
      )}
    </div>
  );
}
