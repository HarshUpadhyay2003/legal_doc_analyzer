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
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';

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
  const [isNotificationsOpen, setNotificationsOpen] = useState(false);
  const [isHelpOpen, setHelpOpen] = useState(false);

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
      {/* Left side - Mobile menu */}
      <div className="flex items-center space-x-4 flex-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleSidebar}
          className="lg:hidden text-gray-600 dark:text-gray-300"
        >
          <Menu className="h-5 w-5" />
        </Button>
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

        {/* Help Button (Dialog) */}
        <Dialog open={isHelpOpen} onOpenChange={setHelpOpen}>
          <DialogTrigger asChild>
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-foreground hover:text-accent"
              onClick={() => setHelpOpen(true)}
            >
              <HelpCircle className="h-5 w-5" />
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Help & Support</DialogTitle>
              <DialogDescription>
                For any help or support, please contact the developer:<br/>
                <span className="font-semibold">Harsh Upadhyay</span><br/>
                <a href="mailto:mohit1upadhyay@gmail.com" className="text-blue-600 underline">mohit1upadhyay@gmail.com</a>
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>

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
