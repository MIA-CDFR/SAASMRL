import { initializeApp } from "https://www.gstatic.com/firebasejs/12.12.1/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/12.12.1/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyAZlKbh4t9RyDxIQoQeqLfqivzM3co_dyg",
    authDomain: "mia-sa-asm-ar.firebaseapp.com",
    projectId: "mia-sa-asm-ar",
    storageBucket: "mia-sa-asm-ar.firebasestorage.app",
    messagingSenderId: "31304674466",
    appId: "1:31304674466:web:8b66b3747b82a30aa17bfb",
    measurementId: "G-7EQEN29WQH"
  };



// const app = initializeApp(firebaseConfig);
// const db = getFirestore(app);

// export { db };
const app = initializeApp(firebaseConfig);

export const db = getFirestore(app);