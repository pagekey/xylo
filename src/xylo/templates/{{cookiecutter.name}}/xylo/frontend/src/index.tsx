import React from 'react';


export const HomePage = function() {
    const [message, setMessage] = React.useState<string>("Loading...");
    React.useEffect(() => {
        fetch("http://localhost:5000/").then(resp => resp.json()).then(data => {
            setMessage(data.message);
        })
    }, []);
    return (
        <div>
            <div>
                HOME! Hello Xylo. <a href="/about">About page here</a>
            </div>
            <div>Message: {message}</div>
        </div>
    )
};

export const AboutPage = function() {
    return (
        <div>
            ABOUT! Hello Xylo. <a href="/">Home page here.</a>
        </div>
    )
};
