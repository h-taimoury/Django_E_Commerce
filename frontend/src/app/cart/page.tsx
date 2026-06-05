"use client";

import { useCartStore } from "@/store/cartStore";
import { useEffect, useState } from "react";
import { CartItem } from "./_components/CartItem";
import { CartSummary } from "./_components/CartSummary";
import { EmptyCart } from "./_components/EmptyCart";

export default function CartPage() {
  const cart = useCartStore((state) => state.cart);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return <div className="p-10 text-center">Loading...</div>;
  if (cart.length === 0) return <EmptyCart />;

  const subtotal = cart.reduce(
    (acc, item) => acc + Number(item.price) * item.quantity,
    0,
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-8 text-slate-900">
        Your Shopping Cart
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 items-start">
        <div className="lg:col-span-2 space-y-4">
          {cart.map((item) => (
            <CartItem key={item.id} item={item} />
          ))}
        </div>

        <div className="lg:col-span-1">
          <CartSummary subtotal={subtotal} />
        </div>
      </div>
    </div>
  );
}
