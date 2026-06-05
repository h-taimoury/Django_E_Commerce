"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ShoppingCart, CreditCard } from "lucide-react";

interface CartSummaryProps {
  subtotal: number;
}

export function CartSummary({ subtotal }: CartSummaryProps) {
  const router = useRouter();

  // Basic math logic
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  return (
    <Card className="bg-gray-50 border-none shadow-none rounded-2xl sticky top-24">
      <CardHeader>
        <CardTitle className="text-xl">Cart Summary</CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Breakdown */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Subtotal</span>
            <span className="text-foreground font-medium">
              ${subtotal.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Estimated Tax (10%)</span>
            <span className="text-foreground font-medium">
              ${tax.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Shipping</span>
            <span className="text-green-600 font-medium">Free</span>
          </div>
        </div>

        {/* Total Price */}
        <div className="flex justify-between font-bold text-xl pt-4 border-t border-gray-200">
          <span>Total</span>
          <span>${total.toFixed(2)}</span>
        </div>
      </CardContent>

      <CardFooter className="flex flex-col gap-3">
        {/* Primary Action: Checkout */}
        <Button
          onClick={() => router.push("/checkout")}
          className="w-full bg-[#FFD814] text-black hover:bg-[#F7CA00] rounded-full py-6 font-bold shadow-sm transition-all flex items-center gap-2 border-b-2 border-[#e6c212] active:border-b-0"
        >
          <CreditCard size={18} />
          Checkout
        </Button>

        {/* Secondary Action: Continue Shopping */}
        <Button
          variant="outline"
          onClick={() => router.push("/")}
          className="w-full rounded-full py-6 font-semibold border-gray-300 hover:bg-gray-100 transition-colors flex items-center gap-2"
        >
          <ShoppingCart size={18} />
          Continue Shopping
        </Button>
      </CardFooter>
    </Card>
  );
}
