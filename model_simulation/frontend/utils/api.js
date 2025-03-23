import axios from 'axios';
const API_URL = "http://localhost:8000";

export const purchaseEnergy = ({type, amount}) =>
  axios.post(`${API_URL}/purchase`, {type, amount});
