import ProductCard from "./_components/ProductCard";

type Product = {
  id: number;
  name: string;
  price: number;
  main_image: string;
};

async function getProducts(): Promise<Product[]> {
  const res = await fetch("http://127.0.0.1:8000/api/products/");

  if (!res.ok) {
    throw new Error("Failed to fetch products");
  }

  return res.json();
}

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <main className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8">Products</h1>

      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </main>
  );
}
