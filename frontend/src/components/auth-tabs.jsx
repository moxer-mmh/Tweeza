"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

export default function AuthTabs() {
  const pathname = usePathname()

  const isLoginActive = pathname === "/login"
  const isRegisterActive = pathname.includes("/register")

  return (
    <div className="flex border-b mb-6">
      <Link
        href="/login"
        className={cn(
          "text-sm font-medium pb-2 px-4",
          isLoginActive ? "text-red-700 border-b-2 border-red-700" : "text-gray-600",
        )}
      >
        Login
      </Link>
      <Link
        href="/register"
        className={cn(
          "text-sm font-medium pb-2 px-4",
          isRegisterActive ? "text-red-700 border-b-2 border-red-700" : "text-gray-600",
        )}
      >
        Register
      </Link>
    </div>
  )
}

