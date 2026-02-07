from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c257a31b2dd4"
down_revision = "Null"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        "orders",
        sa.Column(
            "payment_method",
            sa.Enum("stripe", "cod", name="paymentmethod"),
            nullable=False,
            server_default="cod",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "payment_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "stripe_payment_intent_id",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("orders", "stripe_payment_intent_id")
    op.drop_column("orders", "payment_status")
    op.drop_column("orders", "payment_method")
