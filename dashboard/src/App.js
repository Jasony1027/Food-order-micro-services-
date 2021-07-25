import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
export default function App() {
  const statsApiURL =
    "http://acit-3855-kafka.westus2.cloudapp.azure.com:8100/stats";
  const pickupApiUrl =
    "http://acit-3855-kafka.westus2.cloudapp.azure.com:8110/pickup?index=0";
  const deliveryApiUrl =
    "http://acit-3855-kafka.westus2.cloudapp.azure.com:8110/delivery?index=0";
  const imgURL =
    "https://www.freelogodesign.org/file/app/client/thumb/79709edb-2b24-48ff-9037-79ce54be60c5_200x200.png?1605156478449";
  const [data, setData] = useState({ stats: {}, pickup: {}, delivery: {} });
  useEffect(() => {
    const interval = setInterval(() => {
      axios.all([
          axios.get(statsApiURL),
          axios.get(pickupApiUrl),
          axios.get(deliveryApiUrl),
        ])
        .then((arr) => {
          setData({
            stats: arr[0].data,
            pickup: arr[1].data,
            delivery: arr[2].data,
          });
        });
    }, 2000);
  }, [setData]);

  return (
    <div className="App">
      <br />
      <img src={imgURL} alt="food-app" width={150} height={150} />
      <h3 className="stats">Number of orders: {data.stats.num_orders}</h3>
      <h3>-----------------------------------------</h3>
      <h3 className="type">Pickup</h3>
      <h4 className="stats">
        Number of Pickup orders: {data.stats.num_pickup_orders}
      </h4>
      <h4 className="stats">
        Max Pickup Distance: {data.stats.max_pickup_distance}
      </h4>
      <h4 className="stats">
        Min Pickup Distance: {data.stats.min_pickup_distance}
      </h4>
      <h3>-----------------------------------------</h3>
      <h3 className="type">Delivery</h3>
      <h4 className="stats">
        Number of Delivery orders: {data.stats.num_delivery_orders}
      </h4>
      <h4 className="stats">
        Max Delivery Distance: {data.stats.max_delivery_distance}
      </h4>
      <h4 className="stats">
        Min Delivery Distance: {data.stats.min_delivery_distance}
      </h4>
      <h3>-----------------------------------------</h3>
      <div className="update">
        <p>Last Updated: {data.stats.timestamp_delivery}</p>
      </div>
      <h3>-----------------------------------------</h3>
      <h3 className="stats">First Pickup order</h3>
      <div className="update">
        <p>Order ID: {data.pickup.order_id}</p>
        <p>Orderer ID : {data.pickup.orderer.orderer_id}</p>
        <p>
          Distance To Restaurant: {data.pickup.orderer["distance_to_restaurant"]}
        </p>
        <p>Restaurant ID: {data.pickup.restaurant.restaurant_id}</p>
        <p>Restaurant Address: {data.pickup.restaurant.restaurant_address}</p>
        <p>Timestamp: {data.pickup.timestamp}</p>
      </div>
      <h3>-----------------------------------------</h3>
      <h3 className="stats">First Delivery order</h3>
      <div className="update">
        <p>Order ID: {data.delivery.order_id}</p>
        <p>Orderer ID : {data.delivery.orderer.orderer_id}</p>
        <p>
          Distance To Restaurant: {data.delivery.orderer.distance_to_restaurant}
        </p>
        <p>Restaurant ID: {data.delivery.restaurant.restaurant_id}</p>
        <p>Restaurant Address: {data.delivery.restaurant.restaurant_address}</p>
        <p>Timestamp: {data.delivery.timestamp}</p>
      </div>
    </div>
  );
}
