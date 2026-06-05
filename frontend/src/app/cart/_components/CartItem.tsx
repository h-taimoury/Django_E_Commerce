"use client";

import { useCartStore } from "@/store/cartStore";
import { Trash2, Plus, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";

interface CartItemProps {
  item: {
    id: number;
    name: string;
    price: number;
    main_image: string;
    quantity: number;
  };
}

export function CartItem({ item }: CartItemProps) {
  const { removeFromCart, increaseQuantity, decreaseQuantity } = useCartStore();

  const itemPrice = Number(item.price) || 0;

  return (
    <div className="flex flex-col sm:flex-row items-center gap-6 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
      <div className="w-24 h-24 shrink-0 bg-gray-50 rounded-lg p-2 relative overflow-hidden">
        <Image
          src={item.main_image}
          alt={item.name}
          fill
          className="object-contain p-2" // p-2 keeps the product from touching the edges
          sizes="96px" // Tells Next.js exactly how wide this image will be
          unoptimized
        />
      </div>
      <div className="flex-1 text-center sm:text-left">
        <h3 className="font-bold text-lg leading-tight">{item.name}</h3>
        <button
          onClick={() => removeFromCart(item.id)}
          className="text-red-500 text-xs flex items-center gap-1 hover:underline mx-auto sm:mx-0 mt-2"
        >
          <Trash2 size={14} /> Remove
        </button>
      </div>
      <div className="flex items-center border border-gray-300 rounded-full bg-gray-50">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => decreaseQuantity(item.id)}
          className="h-8 w-8 rounded-full"
        >
          <Minus size={14} />
        </Button>
        <span className="w-8 text-center font-bold text-sm">
          {item.quantity}
        </span>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => increaseQuantity(item.id)}
          className="h-8 w-8 rounded-full"
        >
          <Plus size={14} />
        </Button>
      </div>
      <div className="text-right min-w-25">
        <p className="font-bold text-lg">
          ${(itemPrice * item.quantity).toFixed(2)}
        </p>
      </div>
    </div>
  );
}
