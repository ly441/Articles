
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
);

CREATE TABLE magazines(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    description TEXT,
    frequency VARCHAR(50) CHECK (frequency IN ('weekly', 'monthly', 'quarterly', 'yearly')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    );

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255)NOT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) CHECK (status IN ('draft', 'published', 'archived')) DEFAULT 'draft',

    author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    magazine_id INTEGER REFERENCES magazines(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

     CONSTRAINT title_min_length CHECK (length(title) >= 5),
    CONSTRAINT content_min_length CHECK (length(content) >= 100)
);

-

CREATE TABLE author_magazine (
    author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    magazine_id INTEGER NOT NULL REFERENCES magazines(id) ON DELETE CASCADE,
    role VARCHAR(50),
    PRIMARY KEY (author_id, magazine_id)
);



CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_magazine ON articles(magazine_id);
CREATE INDEX idx_articles_published ON articles(published_at) WHERE status = 'published';

