"use client";

import { useCartStore } from "@/store/cartStore";
import { Button } from "@/components/ui/button";

interface Product {
  id: number;
  name: string;
  price: number;
  main_image: string;
}

export default function AddToCartButton({ product }: { product: Product }) {
  const addToCart = useCartStore((state) => state.addToCart);

  const handleAddToCart = (e: React.MouseEvent) => {
    // Prevent clicking the button from triggering a parent Link (like to the product detail page)
    e.preventDefault();
    e.stopPropagation();

    addToCart(product);
  };

  return (
    <Button
      onClick={handleAddToCart}
      className="w-fit rounded-full bg-[#FFD814] px-6 text-black hover:bg-[#F7CA00] border border-[#FCD200] shadow-sm text-xs h-8"
    >
      Add to cart
    </Button>
  );
}
