import Link from "next/link";
import Image from "next/image";
// import UserDropdown from "@/components/UserDropDown";
import logo from "../../../public/next.svg";
import { cn } from "@/lib/utils";
import NavLink from "./NavLink";

const linkItems = [
  { title: "Products", href: "/products" },
  { title: "Blog", href: "/blog" },
  { title: "About", href: "/about" },
  { title: "Contact", href: "/contact" },
];
export default function Navbar() {
  return (
    <div className="flex justify-between items-center p-4 lg:px-[10%] border-t-8 border-t-brand-dark ">
      <Link href="/">
        <Image src="/next.svg" alt="Logo" width={200} height={60} />
      </Link>
      <nav className="hidden pr-12 md:flex items-center gap-8 ">
        {linkItems.map((linkItem, index) => (
          <NavLink
            href={linkItem.href}
            className={cn(
              linkItem.title === "Contact" &&
                "bg-brand-dark text-white rounded-md hover:bg-brand-light px-3",
            )}
            key={index}
          >
            {linkItem.title}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
