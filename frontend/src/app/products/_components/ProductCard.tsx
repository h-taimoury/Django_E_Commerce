import { Button } from "@/components/ui/button";
import Image from "next/image";
import Link from "next/link";

type Product = {
  id: number;
  name: string;
  price: number;
  main_image: string; // "http://localhost:8000/media/product_images/main/airpods.jpg"
};

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link
      className="border rounded-xl shadow-sm hover:shadow-md transition"
      href={`products/${product.id}`}
    >
      <div className="aspect-square relative mb-3 overflow-hidden rounded-lg bg-gray-100">
        <Image
          src={product.main_image}
          alt={product.name}
          fill
          unoptimized
          sizes="(max-width: 640px) 100vw,
                 (max-width: 1024px) 50vw,
                 25vw"
          className="object-cover"
        />
      </div>

      <h2 className="font-semibold">{product.name}</h2>
      <p className="text-gray-600">${product.price}</p>

      {/* Add to Cart Button (Amazon Yellow) */}
      <div className="mt-auto py-4 z-10">
        <Button className="w-fit rounded-full bg-[#FFD814] px-6 text-black hover:bg-[#F7CA00] border border-[#FCD200] shadow-sm text-xs h-8">
          Add to cart
        </Button>
      </div>
    </Link>
  );
}
