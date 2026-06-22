import { useAuthStore } from "@/store/authStore";
import { cn } from "@/utils/cn";
import { Menu , X, Zap } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

type NavLink = {
    href: string;
    label: string;
    onClick?: () => void | Promise<void>;
    className?: string;
};

const navLinks: NavLink[] = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/contact', label: 'Contact' },
];

const getAuthLinks = (isAuthenticated: boolean, logout: () => Promise<void>): NavLink[] => 
    isAuthenticated
    ? [
        { href: '/profile', label: 'Profile' },
        { href: '#', label: 'Logout', onClick: logout },
      ]
    : [{ href: '/signup', label: 'Sign Up', className: 'btn-primary' }];


export function Navbar() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { isAuthenticated, logout } = useAuthStore();
    const location = useLocation();

    const authLinks = getAuthLinks(isAuthenticated, logout);
    const isActive = (path: string) => location.pathname === path;

    const handleLinkClick = async (link: NavLink, closeMenu = false) => {
    if (link.onClick) {
      await link.onClick();  // ← Await the async logout
    }
    if (closeMenu) {
      setIsMobileMenuOpen(false);
    }
  };

    return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold">
          <Zap className="h-5 w-5 text-primary" />
          <span>EB-AI</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-6">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                isActive(link.href) ? "text-primary" : "text-muted-foreground"
              )}
            >
              {link.label}
            </Link>
          ))}
          
          {authLinks.map((link) => (
            link.onClick ? (
              <button
                key={link.href}
                onClick={() => handleLinkClick(link)}
                className="text-sm font-medium text-muted-foreground hover:text-primary"
              >
                {link.label}
              </button>
            ) : (
              <Link
                key={link.href}
                to={link.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  link.className === 'btn-primary'
                    ? "bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/70 hover:text-yellow-300"
                    : isActive(link.href) 
                      ? "text-primary" 
                      : "text-muted-foreground",
                  link.className
                )}
              >
                {link.label}
              </Link>
            )
          ))}
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="md:hidden p-2"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {isMobileMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Mobile Menu Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t bg-background px-4 py-4 space-y-4">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={cn(
                "block text-sm font-medium py-2",
                isActive(link.href) ? "text-primary" : "text-muted-foreground"
              )}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          
          <div className="pt-4 border-t space-y-2">
            {authLinks.map((link) => (
              link.onClick ? (
                <button
                  key={link.href}
                  onClick={() => handleLinkClick(link, true)}
                  className="block w-full text-left text-sm font-medium py-2 text-muted-foreground hover:text-primary"
                >
                  {link.label}
                </button>
              ) : (
                <Link
                  key={link.href}
                  to={link.href}
                  className={cn(
                    "block text-sm font-medium py-2",
                    link.className === 'btn-primary'
                      ? "bg-primary text-primary-foreground px-4 py-2 rounded-md"
                      : "text-muted-foreground hover:text-primary"
                  )}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              )
            ))}
          </div>
        </div>
      )}
    </nav>
  );

}