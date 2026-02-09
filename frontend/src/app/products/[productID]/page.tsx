import Image from "next/image";

type ProductPageProps = {
  params: Promise<{ productID: string }>;
};

interface Category {
  id: number;
  name: string;
  slug: string;
}

interface ProductImage {
  id: number;
  image: string;
  order: number;
}

interface Specification {
  id: number;
  attribute_name: string;
  value: string | number | boolean;
}

interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  quantity_on_hand: number;
  quantity_available: number;
  is_active: boolean;
  main_image: string;
  categories: Category[];
  images: ProductImage[];
  specifications: Specification[];
}

async function getProduct(productID: string): Promise<Product> {
  const res = await fetch(`http://localhost:8000/api/products/${productID}/`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch product");
  }
  return res.json();
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { productID } = await params;
  let product: Product | null = null;
  try {
    product = await getProduct(productID);
  } catch (error) {
    return (
      <div className="max-w-2xl mx-auto my-16 text-center text-red-600">
        Failed to load product.
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto my-16 flex flex-col gap-8 p-4">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Main Image and Gallery */}
        <div className="flex flex-col gap-4 md:w-1/2">
          <Image
            src={product.main_image}
            alt={product.name}
            width={600}
            height={400}
            className="rounded-lg w-full object-cover max-h-96 border"
            unoptimized
            priority
          />
          {product.images.length > 0 && (
            <div className="flex gap-2 overflow-x-auto">
              {product.images
                .sort((a, b) => a.order - b.order)
                .map((img) => (
                  <Image
                    key={img.id}
                    src={img.image}
                    alt={product.name + " gallery"}
                    width={80}
                    height={80}
                    className="w-20 h-20 object-cover rounded border"
                    unoptimized
                  />
                ))}
            </div>
          )}
        </div>
        {/* Product Info */}
        <div className="flex-1 flex flex-col gap-4">
          <h1 className="text-3xl font-bold text-gray-800">{product.name}</h1>
          <div className="text-xl text-green-700 font-semibold">
            ${product.price}
          </div>
          <div className="text-gray-600">{product.description}</div>
          <div className="flex flex-wrap gap-2 mt-2">
            {product.categories.map((cat) => (
              <span
                key={cat.id}
                className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium"
              >
                {cat.name}
              </span>
            ))}
          </div>
          <div className="mt-4">
            <span className="font-medium">Available:</span>{" "}
            {product.quantity_available}
          </div>
          <div className="mt-2">
            <span className="font-medium">Specifications:</span>
            <ul className="list-disc ml-6 mt-1">
              {product.specifications.length === 0 && (
                <li className="text-gray-400">No specifications listed.</li>
              )}
              {product.specifications.map((spec) => (
                <li key={spec.id}>
                  {spec.attribute_name}: {String(spec.value)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
