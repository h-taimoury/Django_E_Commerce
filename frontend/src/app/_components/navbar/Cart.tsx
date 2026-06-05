"use client";

import Link from "next/link";
import { useCartStore } from "@/store/cartStore";
import { ShoppingCart } from "lucide-react";

export default function Cart() {
  const totalItems = useCartStore((state) => state.totalItems());
  const hasHydrated = useCartStore((state) => state.hasHydrated);

  // Prevent SSR mismatch
  if (!hasHydrated) {
    return (
      <Link
        href="/cart"
        className="relative flex items-center justify-center p-2"
        aria-label="Cart"
      >
        <ShoppingCart size={24} />
      </Link>
    );
  }

  return (
    <Link
      href="/cart"
      className="relative flex items-center justify-center p-2 hover:opacity-80 transition"
      aria-label="Cart"
    >
      <ShoppingCart size={24} />

      {totalItems > 0 && (
        <span className="absolute -top-1 -right-1 min-w-4.5 h-4.5 px-1 rounded-full bg-red-600 text-white text-xs flex items-center justify-center font-semibold">
          {totalItems}
        </span>
      )}
    </Link>
  );
}
