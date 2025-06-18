import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  Menu,
  User,
  Settings,
  HelpCircle,
  LogOut,
  Moon,
  Sun
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useTheme } from '@/contexts/ThemeContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface HeaderProps {
  onToggleSidebar: () => void;
  sidebarCollapsed: boolean;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar, sidebarCollapsed, onLogout }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [notificationCount] = useState(3);
  const { theme, setTheme, isDark } = useTheme();
  const username = localStorage.getItem('username') || 'User';
  const email = localStorage.getItem('email') || '';

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    // Implement search functionality here
  };

  const handleNotificationClick = () => {
    console.log('Opening notifications');
    // Implement notification panel here
  };

  const handleProfileClick = () => {
    console.log('Opening profile');
  };

  const handleSettingsClick = () => {
    console.log('Opening settings');
  };

  const handleHelpClick = () => {
    console.log('Opening help');
  };

  const handleSignOut = () => {
    onLogout();
    console.log('Signing out');
  };

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark');
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
      {/* Left side - Mobile menu and search */}
      <div className="flex items-center space-x-4 flex-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleSidebar}
          className="lg:hidden text-gray-600 dark:text-gray-300"
        >
          <Menu className="h-5 w-5" />
        </Button>
        
        <form onSubmit={handleSearch} className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search documents, questions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 focus:bg-white dark:focus:bg-gray-600 dark:text-white dark:placeholder-gray-400"
          />
        </form>
      </div>

      {/* Right side - Actions and profile */}
      <div className="flex items-center space-x-4">
        {/* Theme Toggle */}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={toggleTheme}
          className="text-foreground hover:text-accent"
        >
          {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>

        {/* Help Button */}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={handleHelpClick}
          className="text-foreground hover:text-accent"
        >
          <HelpCircle className="h-5 w-5" />
        </Button>

        {/* Notifications */}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={handleNotificationClick}
          className="text-foreground hover:text-accent relative"
        >
          <Bell className="h-5 w-5" />
          {notificationCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
            >
              {notificationCount}
            </Badge>
          )}
        </Button>

        {/* User Profile Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="p-0 h-auto">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/placeholder-avatar.jpg" />
                <AvatarFallback className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                  <User className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
            <div className="px-2 py-1.5">
              <p className="text-sm font-medium dark:text-white">{username}</p>
              {email && <p className="text-xs text-gray-500 dark:text-gray-400">{email}</p>}
            </div>
            <DropdownMenuSeparator className="dark:bg-gray-700" />
            <DropdownMenuItem onClick={handleProfileClick} className="dark:text-white dark:hover:bg-gray-700">
              <User className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleSettingsClick} className="dark:text-white dark:hover:bg-gray-700">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleHelpClick} className="dark:text-white dark:hover:bg-gray-700">
              <HelpCircle className="mr-2 h-4 w-4" />
              Help & Support
            </DropdownMenuItem>
            <DropdownMenuSeparator className="dark:bg-gray-700" />
            <DropdownMenuItem onClick={handleSignOut} className="text-red-600 dark:text-red-400 dark:hover:bg-gray-700">
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};
