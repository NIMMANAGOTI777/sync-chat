import { io } from 'socket.io-client';
import { API_BASE } from './api';

export const connectSocket = (userId) => io(API_BASE, { query: { userId } });
