/**
 * Product Card Component
 * Displays individual product information
 */

import React from 'react';

export interface ProductCardProps {
    id: string;
    name: string;
    description: string;
    price: number;
    category: string;
    stock: number;
    onSelect?: (productId: string) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({
    id,
    name,
    description,
    price,
    category,
    stock,
    onSelect,
}) => {
    const handleSelect = () => {
        if (onSelect) {
            onSelect(id);
        }
    };

    return (
        <div className="product-card">
            <div className="product-header">
                <h3 className="product-name">{name}</h3>
                <span className="product-category">{category}</span>
            </div>

            <p className="product-description">{description}</p>

            <div className="product-footer">
                <div className="product-price">
                    <span className="price-label">Price:</span>
                    <span className="price-amount">${price.toFixed(2)}</span>
                </div>

                <div className="product-stock">
                    <span className={`stock-badge ${stock > 0 ? 'in-stock' : 'out-of-stock'}`}>
                        {stock > 0 ? `${stock} in stock` : 'Out of stock'}
                    </span>
                </div>
            </div>

            {stock > 0 && (
                <button
                    className="product-select-btn"
                    onClick={handleSelect}
                >
                    Select Product
                </button>
            )}

            <div className="product-id">ID: {id}</div>
        </div>
    );
};

export default ProductCard;
