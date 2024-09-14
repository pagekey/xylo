import React from 'react';


export const HomePage = function() {
    return (
        <div>
            HOME! Hello Xylo. <a href="/about">About page here</a>
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
