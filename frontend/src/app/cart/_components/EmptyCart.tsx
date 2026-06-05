"use client";

import Link from "next/link";
import { ShoppingBag, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export function EmptyCart() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center">
      {/* Icon with a soft background */}
      <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6">
        <ShoppingBag size={48} className="text-slate-400" />
      </div>

      {/* Text Content */}
      <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-2">
        Your cart is empty
      </h1>
      <p className="text-slate-500 max-w-87.5 mb-8">
        Looks like you haven&apos;t added anything to your cart yet. Explore our
        products and find something you love!
      </p>

      {/* Call to Action */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Link href="/products">
          <Button className="bg-[#FFD814] text-black hover:bg-[#F7CA00] rounded-full px-8 py-6 font-bold flex items-center gap-2">
            Start Shopping
            <ArrowRight size={18} />
          </Button>
        </Link>
      </div>
    </div>
  );
}
